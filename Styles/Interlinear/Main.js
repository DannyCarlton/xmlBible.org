const XHTML_NS = 'http://www.w3.org/1999/xhtml';

window.onload = function() {
  // Check if the dictionaries have been loaded sucessfully.
  const hasDict = (typeof strongsGreekDictionary === 'object' &&
                   typeof strongsHebrewDictionary === 'object');

  const words = document.getElementsByTagName('word');

  for (const w of words) {
    const strongs = w.getElementsByTagName('strongs')[0];
    const english = w.getElementsByTagName('english')[0];
    const sn = strongs.textContent;
    if (!sn) {
      continue;
    }

    const isHebrew = w.getElementsByTagName('hebrew').length > 0;
    const isGreek = w.getElementsByTagName('greek').length > 0;
    if (!isHebrew && !isGreek) {
      continue;
    }

    let hrefPrefix;
    if (isHebrew) {
      hrefPrefix = 'https://biblehub.com/hebrew';
    } else if (isGreek) {
      hrefPrefix = 'https://biblehub.com/greek';
    }
    const snLinkHTML =
          `<a xmlns="${XHTML_NS}" href="${hrefPrefix}/${sn}.htm">${sn}</a>`;
    strongs.innerHTML = snLinkHTML;

    if (!hasDict) {
      continue;
    }

    let entry;
    if (isHebrew) {
      entry = strongsHebrewDictionary["H"+sn];
    } else if (isGreek) {
      entry = strongsGreekDictionary["G"+sn];
    }

    const sd = document.createElement('strongs-definition');
    sd.innerHTML = `[${snLinkHTML}] `;
    sd.appendChild(document.createTextNode(entry?.strongs_def || ''));
    w.insertBefore(sd, strongs.nextSibling);

    const ed = document.createElement('english-definition');
    ed.appendChild(document.createTextNode(entry?.kjv_def || ''));
    w.insertBefore(ed, english.nextSibling);
  }
}

function loadStrongs() {
  const scripts = [
    "../../Strongs/greek/strongs-greek-dictionary.js",
    "../../Strongs/hebrew/strongs-hebrew-dictionary.js"
  ];
  for (const s of scripts) {
    const script = document.createElementNS(XHTML_NS, 'script');
    script.src = s;
    document.documentElement.appendChild(script);
  }
}

module = {};
loadStrongs();
