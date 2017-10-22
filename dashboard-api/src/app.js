// NodeJS default
const path = require('path');
const fs = require('fs');

// Installed
const express = require('express');
const morgan = require('morgan');
const hbs = require('hbs');
var cors = require('cors');

const app = express();

hbs.registerPartials(__dirname + '/views/partials');

app.set('views', path.join(__dirname, 'views/'));
app.set('view engine', 'hbs');

hbs.registerHelper('getCurrentYear', () => {
  return new Date().getFullYear();
});

/*
 * Replace something in the layout you extend in child
 * Usage: {{{_sections.section_name}}} in the parent
 * Then, you can replace it:
 * {{#section 'section_name'}}
 *   content
 * {{/section}}
 */
hbs.registerHelper('section', (name, options) => {
  if(!this._sections) this._sections = {};
  this._sections[name] = options.fn(this);
  return null;
});

// Setup cors
app.use(cors());

// Setup logger
app.use(morgan(':remote-addr - :remote-user [:date[clf]] ":method :url HTTP/:http-version" :status :res[content-length] :response-time ms'));

// Serve static assets
app.use(express.static(path.resolve(__dirname, '..', 'public')));

// static website routes
app.get('/', (req, res) => {
  res.render('dashboard.hbs');
});

const PORT = process.env.PORT || 8000;

app.listen(PORT, () => {
  console.log(`App listening on port ${PORT}!`);
});

