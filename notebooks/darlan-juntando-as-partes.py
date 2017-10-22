
# coding: utf-8

# In[3]:

import os
import re
import json
import pandas as pd
import numpy as np
from glob import glob
from os import path

from unicodedata import normalize

DIR = '../data'

cities_data = None
with open('../cidades/cities.json') as f:
    cities_data = json.loads(f.read())
    
months  = {
    'de janeiro': 1,
    'de fevereiro': 2,
    'de março': 3,
    'de abril': 4,
    'de maio': 5,
    'de junho': 6,
    'de julho': 7,
    'de agosto': 8,
    'de setembro': 9,
    'de outubro': 10,
    'de novembro': 11,
    'de dezembro': 12,
    '/01/': 1,
    '/02/': 2, 
    '/03/': 3,
    '/04/': 4,
    '/05/': 5,
    '/06/': 6,
    '/07/': 7,
    '/08/': 8,
    '/09/': 9,
    '/10/': 10,
    '/11/': 11,
    '/12/': 12,
}


# In[4]:

def normalized(text):
    try:
        return normalize('NFKD', text).encode('ASCII','ignore').decode('ASCII')
    except:
        pass
    return text


# In[22]:

def document_iterator(DIR):
    for index, file in enumerate(glob(path.join(DIR, '*.txt'))):
        yield (open(file, 'r', encoding='cp1252').read(), file)
        if index >= 1000:
            break


# In[6]:

def get_codigo(filename):
    return re.sub(r"\_.\.txt","",filename.replace(DIR,"")).replace('\\', '')


# In[ ]:




# In[7]:

def get_process_num(content):
    process_num_matches = re.findall(r"proc(?:esso|.)(?:[^\d]{0,15})((?:\d|-|\.|\s\/\s?)*)", content, re.IGNORECASE)
    for match in process_num_matches:
        if match:
            return match
    return None


# In[8]:

def _find_state(text):
    for state in cities_data:
        if state in text:
            return state

    return None


def _find_city(state, text):
    for city in cities_data[state]:
        if city in text:
            return city
    return None


def get_estado_e_comarca(file):
    uf, comarca = None, None
    states = re.findall(r'estado [\w\t\r\n]*\s*[^\n\r]*', file, re.IGNORECASE)
    cities = re.findall(r'comarca\s?\:?[\w\t\r\n\:]*\s*[^\n\r]*', file, re.IGNORECASE)
    if len(states):
        text = ''.join(states[0])
        uf = _find_state(text.lower().strip())
        if len(cities) and uf:
            text = ''.join(cities[0])
            comarca = _find_city(uf.lower().strip(), text.lower().strip())

    return uf, comarca


# In[9]:

def compile_multiple(regexes):
    programs = []
    for regex in regexes:
        programs.append(re.compile(regex, re.IGNORECASE))
    return programs

def varas_identify(text):
    p = re.compile('(^|\W)vara\W', re.IGNORECASE)
    lines = []
    for line in text.splitlines():
        if p.search(line) is not None:
            lines.append(normalized(line.strip()))
    return lines

def varas_filter(lines):
    regexes = ['\d+[ª,a]?.*vara\W', '(^|\W)Vara d[e,o,a]', '(^|\W)Vara:', '(^|\W)Vara civel', '(^|\W)Vara comercial', '(^|\W)Vara regional', '\w+eira vara', 'segunda vara', 'quarta vara', 'quinta vara', 'sexta vara', 'setima vara', 'oitava vara', 'decima vara', 'nona vara', '\w+esima vara', 'vara unica', 'vara judicial']

    programs = compile_multiple(regexes)

    regex_filtered = []
    for text in lines:
        for p in programs:
            if p.search(text) is not None:
                regex_filtered.append(text)
                break
    return regex_filtered

def varas_first(lines):
    if len(lines) > 0:
        return lines[0]
    else:
        return None

def varas_from_matching(line):
    startregexes = ['primeira vara.*', 'segunda vara.*', 'terceira vara.*', 'quarta vara.*', 'quinta vara.*', 'sexta vara.*', 'setima vara.*', 'oitava vara.*', 'decima vara.*', 'nona vara.*', '\w+esima vara.*', '\d+[ª,a]?(.{2}|\s)vara\W.*', 'vara unica', 'vara judicial', '(^|\W)Vara civel .*', '(^|\W)Vara comercial', '(^|\W)Vara regional .*', '(^|\W)Vara .*']

    programs = compile_multiple(startregexes)
    if line is not None:
        for p in programs:
            if p.search(line) is not None:
                return p.search(line).group(0).strip()
    
    return line

def varas_final_value(line):
    p = re.compile('(\s\s+|,|-)')

    if line is not None:
        return p.split(line)[0].strip()
    return line

def get_vara(text):
    lines = varas_identify(text)
    lines = varas_filter(lines)
    line = varas_first(lines)
    vara = varas_from_matching(line)
    vara = varas_final_value(vara)
    return vara


# In[10]:

def clean_blank_lines(lines):
    cleaned_lines = []
    for line in lines:
        copy = line
        re.sub("(\s)+", "", copy)
        if len(copy) > 0:
            cleaned_lines.append(line)
    return cleaned_lines

def starts_with_lower(string):
    if string[0].lower() == string[0]:
        return True
    
def check_name(string):
    bad_words = ['processo', 'sa', 'ltda', 'acao', 'vara', 'juiz', 'autos', 'contratuais', 
             'contratos', 'vistos', 'rua',
            'a', 'ante', 'apos', 'ate', 'com', 'contra', 'em', 'entre', 
            'para', 'per', 'por', 'perante', 'sem', 'sob', 'sobre', 'tras']

    words = re.split("\W",string)
    words = [word for word in words if word != ""] 
    if len(words) < 2 or len(words) > 6: #supondo que o nome completo de uma pessoa deve ter mais de uma palavra
        return False
    if starts_with_lower(words[0]): #supondo que a primeira letra de todas mesmo do nome TEM que ser maiuscula
        return False
    last_lower = False
    for word in words:
        if word.lower() in bad_words:
            return False
        if len(word) < 2:
            return False
        if len(word) < 3: #eh razoavel supor que um nome deve ter mais que 2 caracteres
            continue
        first_letter_is_lower = starts_with_lower(word)
        if first_letter_is_lower and last_lower: #primeira letra minuscula, provavelmente nao eh um nome
            return False
        last_lower = first_letter_is_lower
    if string.upper() == string: #supondo que se eh tudo maiusculo e nao caiu nos outros casos
        return True
    return True

def check_possible_names(possible_names):
    probable = None
    for possible_name in possible_names:
        if not probable:
            if check_name(possible_name):
                probable = possible_name
                break
            sentences = re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', possible_name)
            for sentence in sentences:
                if check_name(sentence):
                    probable = sentence
                    break
    return probable

def find_name(line):
    probable = None
    normalized_s = normalized(line)
    possible_names = re.findall('[a-zA-Z\s]+', normalized_s)
    probable = check_possible_names(possible_names)
    if not probable:
        possible_names = re.findall('[A-Z\s]+', normalized_s)
        probable = check_possible_names(possible_names)
    return probable

def final_name(string):
    return string.strip().upper()

def get_name_from_signature(line):
    name = None
    #CASO Este documento foi assinado digitalmente por [nome do juiz]
    assinatura_re = re.findall('Este documento foi assinado digitalmente por', line)
    if assinatura_re:
        rest = line.replace('Este documento foi assinado digitalmente por ', '')
        has_name = find_name(rest)
        if has_name:
            name = final_name(has_name)
    return name

# Pattern 1: [nome do juiz] + "Juiz de Direito" na mesma linha
def find_judge_string(name, text): 
    found = re.findall('juiz.*de.*direito.*', text.lower())
    if found:
        return final_name(name)
    found = re.findall('ajuiz', text.lower())
    if found:
        return final_name(name)
    
def get_line_name(i,line, lines):
    qt_lines = len(lines)
    name = get_name_from_signature(line)
    if name:
        return name
    has_name = find_name(line)
    if has_name:
        name = find_judge_string(has_name, line)
        if name:
            return name
        if i+1 != qt_lines:
            name = find_judge_string(has_name, lines[i+1])
        if name:
            return name
        if i != 0:
            name = find_judge_string(has_name, lines[i-1])
    return name

def get_name(lines):
    name = None
    qt_lines = len(lines)
    for i, line in enumerate(lines):
        if name:
            break
        name = get_line_name(i,line,qt_lines)
    return name

def not_judge(text):
    found = re.findall('art.*40.*Lei.*9\.099/95', text)
    if found:
        return True
    return False


# In[11]:

def get_juiz(text):
    name = None
    if not_judge(text):
        return 'LEIGO'
        
    lines = text.splitlines()
    lines = clean_blank_lines(lines)
    for i, line in enumerate(lines):
        if name:
            break
        name = get_line_name(i, line, lines)
    return name


# In[12]:

def get_author(content):
    content = normalized(content)
    author_matches = re.findall(r"(?:(?:a|A)utora?|AUTORA?|(?:R|r)equerente|REQUERENTE|(?:(?:P|p)romovente|PROMOVENTE)\(?(?:S|s)?\)?|(?:D|d)emandante|DEMANDANTE)(?:[^A-Z])*([A-Z][^\n]*)|(?:(?:V|v)istos?|VISTOS?)(?:[^A-Z]*)([A-Z\s][^a-z]*)", content)
    for match in author_matches:
        for author in match:
            if author:
                author = re.sub('[^\w\s]','',author).lower()
                if len(author) > 4 and re.search('(\s\s+|[0-9])', author) is None:
                    return author.strip()
    return None


# In[13]:

def get_lawyer(content):
    lawyer_matches = re.findall(r"(?:Adv(?:ogado)?(?:\(a\))?|Procurador)\W[^A-Z]*([A-Z][^\n(-]*)", content)
    lawyers = []

    for lawyer in lawyer_matches:
        if lawyer and len(lawyer.split()) <= 5:
            lawyers.append(lawyer.strip())
        
    return '/'.join(lawyers).lower() if lawyers else None


# In[14]:

def tipo_financiamento(text):
    tipo = {
        ' consignado': re.compile('(^|\W)consignado.*', re.IGNORECASE),
        ' de veiculo': re.compile('((^|\W)veiculo.*|(^|\W)carro.*|(^|\W)automove.*|(^|\W)onibus.*|(^|\W)moto\W.*|(^|\W)motocicleta.*)', re.IGNORECASE),
    }
    
    for key in tipo:
        if tipo[key].search(text) is not None:
            return key
    
    return ''

def get_produto(text):
    text = normalized(text)
    matches = []
    regex_financiamento = '((^|\W)d?[o,e,a]((^|\W)financia\w*.*|(^|\W)emprest.*)|contrato de((^|\W)financia\w*.*|(^|\W)emprest.*)|((^|\W)financia\w+|(^|\W)emprestimo)\Wcontratado)'
    regex_cartao = '((^|\W)credito.*(^|\W)cartao.*|(^|\W)cartao.*(^|\W)credito.*)'
    financiamento = re.compile(regex_financiamento, re.IGNORECASE)
    cartao = re.compile(regex_cartao, re.IGNORECASE)
    
    if financiamento.search(text) is not None:
        matches = ['financiamento'+tipo_financiamento(text)]
    if cartao.search(text) is not None:
        matches.append('cartao de credito')
            
    return '/'.join(matches)


# In[15]:

def find_argumento(sentences):
    p = re.compile('(^|\W)contest\w+\W|(^|\W)aleg[a,o]\w*\W', re.IGNORECASE)
    first = last = -1
    for index, sentence in enumerate(sentences):
        if p.search(sentence) is not None:
            if first < 0:
                first = index
                last = index
            else:
                last = index
    return first, last

def filter_argumento(sentences):
    p = re.compile('\w*procede\w*', re.IGNORECASE)
    res = []
    for sentence in sentences:
        if p.search(sentence) is None:
            sentence = sentence.strip().replace('\n', ' ').replace('\r', '')
            res.append(sentence)
    return res

def get_argumento(text):
    text = normalized(text)
    sentences = text.split('.')
    first, last = find_argumento(sentences)
    if first >= 0:
        res = sentences[first:last]
        filtered = filter_argumento(res)
        if len(filtered) > 0:
            return '.'.join(filtered)
        
    sentences = filter_argumento(sentences)
    
    return '. '.join(sentences)


# In[16]:

def get_target(text):
    match = re.search(r'.{20}parcialmente.{20}', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group()

def get_target(text):
    procedente_positions = [m.start() for m in re.finditer(' procedente', text, re.IGNORECASE)]
    improcedente_positions = [m.start() for m in re.finditer('improcedente', text, re.IGNORECASE)]
    if len(improcedente_positions) > 0 and len(procedente_positions) == 0: 
        return 1
    
    elif len(improcedente_positions) == 0 and len(procedente_positions) > 0: 
        return 0
    
    elif len(improcedente_positions) > 0 and len(procedente_positions) > 0:
        return int(improcedente_positions[-1] > procedente_positions[-1])
    else:
        return 0


# In[17]:

def get_motivo_frequency(text):
    result_ind = re.findall(r'indenizacao|dano moral|negativacao|reparacao de danos|fraudulento|fraude|lucro cessante|dano material', text, re.DOTALL | re.IGNORECASE)
    result_rev = re.findall(r'revisao|clausulas contratuais|comissao de permanencia|juros moratorios|encargos', text, re.DOTALL | re.IGNORECASE)
    result_tarifa = re.findall(r'Repeticao de indebito|Tarifa de cadastro|Servicos de terceiros|Custo efetivo total|Tarifas', text, re.DOTALL | re.IGNORECASE)
    return (len(result_ind), len(result_rev), len(result_tarifa))

def get_motivo(text):
    text = normalized(text)
    ind, rev, tarifa = get_motivo_frequency(text)
    if ind > rev and ind > tarifa:
        return (ind, rev, tarifa, 'indenizacao')
    if rev > ind and rev > tarifa:
        return (ind, rev, tarifa, 'revisao')
    if tarifa > rev and tarifa > ind:
        return (ind, rev, tarifa, 'tarifa')
    else:
        return (ind, rev, tarifa, np.nan)


# In[ ]:




# In[34]:

def get_date(text):
    text = text.lower()
    linha_total = 0
    linha_achou = 0
    lines = text.splitlines()
    dia, mes, ano = None, None, None
    for index, line in enumerate(lines):
    #procura de linha a linha a palavra mes
        for month in months:
            left,sep,right = line.partition(month)
            if sep: # True iff 'something' in line
                ano = re.findall(r'\d+', right) #deixa apenas os numeros no string da direita
                dia = re.findall(r'\d+', left)
                mes = sep
                linha_achou = index #encontra ultima linha em que achou o mes
        
    #normalmente a data real esta no final do documento. Entao, se a linha em que 
    #achou mes esta entre as ultimas 15, provavelmente eh a data do arquivo
    #isso evita que pegue uma data qualquer no meio do texto
    if linha_achou > len(lines) - 15:
        if len(dia) > 0:
            dia = dia[-1]
        if len(ano) > 0:
            ano = ano[0]
        mes = months.get(mes, 1)
        
        #se os dias e anos foram razoaveis, coloca no .txt
        if ano and int(ano) > 1990 and int(ano) < 2018:
            if not dia or int(dia) < 1 or int(dia) > 31:
                dia = 1
            return '%s/%s/%s' % (dia, mes, ano)
        
    return None


# In[38]:

def get_data_from(filename, text):
    result = dict()
    result['codigo'] = get_codigo(filename)
    result['nro'] = get_process_num(text)
    uf, comarca = get_estado_e_comarca(text)
    result['uf'] = uf
    result['comarca/cidade'] = comarca
    result['vara'] = get_vara(text)
    result['juiz'] = get_juiz(text)
    result['autor'] = get_author(text)
    result['data'] = get_date(text)
    result['advogado'] = get_lawyer(text)
    indenizacao, revisao, tarifa, tipo = get_motivo(text)
    result['indenizacao_count'] = indenizacao
    result['revisao_count'] = revisao
    result['tarifa_count'] = tarifa
    result['motivo'] = tipo
    result['produto'] = get_produto(text)
    result['argumentos'] = get_argumento(text)
    result['target'] = get_target(text)
    
    return result
    


# In[40]:

from concurrent.futures import ProcessPoolExecutor, as_completed

result = {
    'codigo': [],
    'nro': [],
    'uf': [],
    'comarca/cidade': [],
    'vara': [],
    'juiz': [],
    'autor': [],
    'data': [],
    'advogado': [],
    'indenizacao_count': [],
    'revisao_count': [],
    'tarifa_count': [],
    'motivo': [],
    'produto': [],
    'argumentos': [],
    'target': [],
}


futures = []
for text, filename in document_iterator(DIR):
    with ProcessPoolExecutor() as executor:
        futures.append(executor.submit(get_data_from,filename, text))
        
    for index, future in enumerate(as_completed(futures)):
        if index % 10 == 0:
            print('Processed %s files of %s' % (index+1, len(futures)))
        data = future.result()
        for key in data:
            result[key].append(data[key])
    

pd.DataFrame(result).to_csv('sample_1000_parallel.csv', index=False)

