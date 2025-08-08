function transpose(semitones) {
    const content = document.getElementById("song-content");
    const text = content.textContent;
    const transposed = text.replace(/\[([A-G][#b]?m?7?(sus[24])?(add[24679])?)\]/g, (match, chord) => {
        return '[' + transposeChord(chord, semitones) + ']';
    });
    content.textContent = transposed;
}

const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const flatToSharp = {'Db':'C#','Eb':'D#','Gb':'F#','Ab':'G#','Bb':'A#'};

function renderChord(container, chordData) {
  const wrapper = document.createElement("div");

  wrapper.className = "chord-box";
  const div = document.createElement("div");
  wrapper.appendChild(div);
 // info doit avoir une clé 'chord' avec un tableau de positions:contentReference[oaicite:1]{index=1}
  const box = new vexchords.ChordBox(div, { width: 120, height: 160,  bgColor: '#333',     // fond du diagramme
  defaultColor: '#fff',// couleur des marqueurs
  stringColor: '#ccc', // cordes en gris clair
  fretColor: '#ccc',   // frettes en gris clair
  textColor: '#eee'    // texte en gris clair
   });
  container.appendChild(wrapper);
  box.draw(chordData);

    //const chord = new vexchords.Chord(chordData);
    //chord.addModifier(new vexchords.Modifier("position", chordData.position || 1));
    //chord.draw(container);
}

function update_chord_diagram(name, direction) {
    const box = document.getElementById(`chord-${name}`);
    const svgContainer = box.querySelector(".chord-diagram");

    const positions = chordShapes[name];
    const currentIndex = chordShapes[name].currentIndex || 0;

    const newIndex = (currentIndex + direction + positions.length) % positions.length;
    chordShapes[name].currentIndex = newIndex;

    // Clear previous SVG
    svgContainer.innerHTML = "";

    renderChord(svgContainer, positions[newIndex]);
}
function transposeChord(chord, semitones) {
    for (let flat in flatToSharp) {
        chord = chord.replace(flat, flatToSharp[flat]);
    }
    const match = chord.match(/^([A-G]#?)(.*)$/);
    if (!match) return chord;
    let idx = notes.indexOf(match[1]);
    if (idx === -1) return chord;
    let newIdx = (idx + semitones + 12) % 12;
    return notes[newIdx] + match[2];
}


const chordShapes = {}
function append_to_container(container, name, positions, currentIndex = 0) {
    const box = document.createElement("div");
    box.className = "chord-box";
    box.id = `chord-${name}`;

    const title = document.createElement("div");
    title.className = "name";
    title.textContent = name;
    box.appendChild(title);

    const svgContainer = document.createElement("div");
    svgContainer.className = "chord-diagram";
    box.appendChild(svgContainer);

    // Add navigation controls if multiple positions
    if (positions.length > 1) {
        const nav = document.createElement("div");
        nav.style.marginTop = "4px";

        const prevBtn = document.createElement("button");
        prevBtn.textContent = "⟵";
        prevBtn.onclick = () => update_chord_diagram(name, -1);
        nav.appendChild(prevBtn);

        const nextBtn = document.createElement("button");
        nextBtn.textContent = "⟶";
        nextBtn.onclick = () => update_chord_diagram(name, 1);
        nav.appendChild(nextBtn);

        box.appendChild(nav);
    }

    container.appendChild(box);

    // Store current index
    if (!chordShapes[name].currentIndex) {
        chordShapes[name].currentIndex = currentIndex;
    }

    renderChord(svgContainer, positions[currentIndex]);
}
function append_to_container_(container, name, info) {
  const wrapper = document.createElement("div");
  wrapper.className = "chord-box";
  const label = document.createElement("div");
  label.className = "name";
  label.textContent = name;
  wrapper.appendChild(label);

  const div = document.createElement("div");
  wrapper.appendChild(div);

  // info doit avoir une clé 'chord' avec un tableau de positions:contentReference[oaicite:1]{index=1}
  const box = new vexchords.ChordBox(div, { width: 120, height: 160,  bgColor: '#333',     // fond du diagramme
  defaultColor: '#fff',// couleur des marqueurs
  stringColor: '#ccc', // cordes en gris clair
  fretColor: '#ccc',   // frettes en gris clair
  textColor: '#eee'    // texte en gris clair
   });
  container.appendChild(wrapper);
  box.draw(info);

}
function getPopup() {
  let popup = document.getElementById('chord-popup');
  if (!popup) {
    popup = document.createElement('div');
    popup.id = 'chord-popup';
    document.body.appendChild(popup);
  }
  return popup;
}
function display_chords()
{
    const chordData = JSON.parse(document.getElementById("chord-data").textContent);
    const container = document.getElementById("chords");
    for (const [name, positions] of Object.entries(chordData)) {
          // VexChords est exposé globalement sous le nom "vexchords"
          chordShapes[name] = positions;  // store all positions
          append_to_container(container,name, positions)

        }
}
function display_chordss()
{
 // récupère la liste des accords depuis l'API
    fetch("/api/chords")
      .then(resp => resp.json())        // parse le JSON:contentReference[oaicite:3]{index=3}
      .then(data => {
        const container = document.getElementById("chords");
        // pour chaque accord, créer une boîte et dessiner le diagramme
        for (const [name, info] of Object.entries(data)) {
          // VexChords est exposé globalement sous le nom "vexchords"
          append_to_container(container,name, info)
          chordShapes[name] = info
        }
      })
      .catch(err => console.error("Erreur lors du chargement des accords:", err));
}

function showDiagram(chordName) {
  console.log('showDiagram called with:', chordName);
  const info = chordShapes[chordName];
  if (!info) return;

  const popup = getPopup();
  popup.innerHTML = '';               // vide le contenu
  popup.style.display = 'block';      // le rendre visible

  // Positionner le pop-up juste à droite de l'élément survolé
  const rect = event.target.getBoundingClientRect();
  const scrollTop  = window.pageYOffset || document.documentElement.scrollTop;
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
  popup.style.left = (scrollLeft + rect.right + 8) + 'px';
  popup.style.top  = (scrollTop + rect.top) + 'px';

  // Insérer le titre puis le diagramme
  const title = document.createElement('div');
  title.textContent = chordName;
  title.style.textAlign = 'center';
  title.style.marginBottom = '0.3em';
  popup.appendChild(title);
  console.log('append_to_container called with:', chordName,info);
  append_to_container(popup, chordName, info);

}

function hideDiagram() {
  console.log('hideDiagram');
  const container = document.getElementById("chord-popup");
  if (container) container.style.display = "none";
}

window.onload = function() {
    const raw = JSON.parse(document.getElementById("raw-song").textContent);
    const content = document.getElementById("song-content");
    const chordRe = /\[([A-G][^\]]*)\](\S+)/g;
    const html = raw.replace(chordRe, (match, chord, lyric) => {
    return `<span class="chunk" onmouseenter="showDiagram('${chord}')" onmouseleave="hideDiagram()"><span class="chord-label">${chord}</span>${lyric}</span>`;
});
    content.innerHTML = html;
};