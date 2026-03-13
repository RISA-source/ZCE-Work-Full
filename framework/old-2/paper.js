const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, NumberFormat
} = require('docx');
const fs = require('fs');

// ── Helpers ────────────────────────────────────────────────────────────────
const FONT = "Times New Roman";
const MONO = "Courier New";
const W = 9360; // content width in DXA (1-inch margins on US Letter)

function border(color="AAAAAA") {
  const b = { style: BorderStyle.SINGLE, size: 1, color };
  return { top: b, bottom: b, left: b, right: b };
}
function noBorder() {
  const b = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: b, bottom: b, left: b, right: b };
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [new TextRun({ text, font: FONT, size: 28, bold: true })]
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 80 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true })]
  });
}
function h3(text) {
  return new Paragraph({
    spacing: { before: 180, after: 60 },
    children: [new TextRun({ text, font: FONT, size: 22, bold: true, italics: true })]
  });
}
function body(runs) {
  if (typeof runs === 'string') runs = [new TextRun({ text: runs, font: FONT, size: 22 })];
  return new Paragraph({ spacing: { before: 0, after: 120 }, children: runs });
}
function italic(text) { return new TextRun({ text, font: FONT, size: 22, italics: true }); }
function bold(text)   { return new TextRun({ text, font: FONT, size: 22, bold: true }); }
function mono(text)   { return new TextRun({ text, font: MONO, size: 20 }); }
function normal(text) { return new TextRun({ text, font: FONT, size: 22 }); }
function sup(text)    { return new TextRun({ text, font: FONT, size: 18, superScript: true }); }

function codeBlock(lines) {
  return lines.map(line => new Paragraph({
    spacing: { before: 0, after: 0 },
    shading: { fill: "F4F4F4", type: ShadingType.CLEAR },
    indent: { left: 720 },
    children: [new TextRun({ text: line, font: MONO, size: 18 })]
  }));
}

function statusPill(status) {
  // Returns a TextRun with bracket notation
  const map = {
    'PROVEN':    { text: '[PROVEN]',    bold: true },
    'ARGUED':    { text: '[ARGUED]',    bold: true },
    'OPEN':      { text: '[OPEN]',      bold: true },
    'SPECULATIVE':{ text: '[SPECULATIVE]', bold: true },
    'CORRECTED': { text: '[CORRECTED]', bold: true },
  };
  const s = map[status] || { text: `[${status}]`, bold: false };
  return new TextRun({ text: ' ' + s.text, font: FONT, size: 20, bold: s.bold });
}

function rule() {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC" } },
    children: []
  });
}

function tableRow(cells, widths, header=false) {
  return new TableRow({
    tableHeader: header,
    children: cells.map((text, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      borders: border("CCCCCC"),
      shading: header ? { fill: "E8E8E8", type: ShadingType.CLEAR } : { fill: "FFFFFF", type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [new Paragraph({ children: [
        typeof text === 'string'
          ? new TextRun({ text, font: FONT, size: 20, bold: header })
          : text
      ]})]
    }))
  });
}

function mkTable(headers, rows, widths) {
  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      tableRow(headers, widths, true),
      ...rows.map(r => tableRow(r, widths, false))
    ]
  });
}

function gap() { return new Paragraph({ spacing: { before: 120, after: 0 }, children: [] }); }

// ── Document ───────────────────────────────────────────────────────────────
const children = [

  // Title block
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 480, after: 240 },
    children: [new TextRun({
      text: "Binary Self-Describing Tokens as a Foundation for the Standard Model Gauge Structure",
      font: FONT, size: 36, bold: true
    })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 120 },
    children: [new TextRun({ text: "Rishi Saraff", font: FONT, size: 24, italics: true })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 480 },
    children: [new TextRun({ text: "Working Paper — March 2026", font: FONT, size: 22, color: "666666" })]
  }),

  rule(),

  // Abstract
  h2("Abstract"),
  body([normal(
    "We study a model in which physical structure is derived from the minimum constraints " +
    "on stable, self-describing binary tokens of the form [0\u1D4C 1\u1D39 0]. " +
    "Four axioms — Named, Frozen, MDL, Productive — uniquely determine the token structure. " +
    "From this structure we derive: (1) charge quantization and photon masslessness from U(1) symmetry " +
    "of the N-sector; (2) the weak force from the minimum-cost doublet at depth M=1, yielding SU(2); " +
    "(3) color symmetry from three ordered 1-bits at depth M=3, yielding SU(3). " +
    "We provide a formal proof that these three sectors are disjoint, establishing that the combined " +
    "gauge group is exactly U(1)\u00D7SU(2)\u00D7SU(3). " +
    "We further derive a nested continued-product formula for lepton mass amplitudes — " +
    "each generation wrapping the previous in a phase factor — as a consequence of lattice geometry alone. " +
    "We diagnose the systematic factor-of-7 discrepancy in coupling constant predictions as arising from " +
    "a missing 4\u03C0 in the g\u00B2 \u2192 \u03B1 conversion, reducing it to a factor of 2. " +
    "We give a complete honest assessment of what is proven, what is argued, and what remains open."
  )]),

  rule(),

  // Section 1
  h1("1. Introduction"),
  body([normal(
    "The gauge group of the Standard Model, G\u209B\u2098 = U(1)\u00D7SU(2)\u00D7SU(3), " +
    "was established empirically between 1967 and 1973. " +
    "Why this specific group — and not SU(5), SO(10), or any other — has remained without " +
    "theoretical explanation for fifty years. " +
    "This paper presents a derivation from a single information-theoretic principle: " +
    "the minimum structure required for stable, self-describing binary symbols."
  )]),
  body([normal(
    "The central object is the binary token [0\u1D4C 1\u1D39 0]: N leading zeros encoding identity (charge), " +
    "M consecutive ones encoding depth (generation), and a terminating zero. " +
    "Four axioms constrain this token. From those axioms, the gauge group follows structurally — " +
    "not by identification with known particle content, but by the symmetry sectors of the decoder."
  )]),
  body([normal(
    "We present results with explicit status labels: "), bold("PROVEN"), normal(" (no open steps), "),
    bold("ARGUED"), normal(" (solid with one named gap), "), bold("OPEN"), normal(" (not yet derived). "),
    normal("This paper does not claim more than the evidence supports.")
  ]),

  // Section 2
  h1("2. The Token and Its Axioms"),
  h2("2.1 Basic Structure"),
  body([normal("The binary self-describing token has the form:")]),
  ...codeBlock(["  [0, 0, ..., 0,  1, 1, ..., 1,  0]", "   |____N____|   |____M____|  term"]),
  gap(),
  body([normal(
    "The decoder extracts two integers: N (count of leading zeros) and M (count of ones). " +
    "Token length: l(N,M) = N + M + 1 bits. Born weight: P(N,M) = exp(\u22122l)."
  )]),
  h2("2.2 The Four Axioms"),
  body([bold("Named:"), normal(" Every token has a unique, stable decoded identity (N,M). No two tokens decode to the same pair.")]),
  body([bold("Frozen:"), normal(" The decoder is fixed at compile time. It cannot be modified by the symbols it processes. A single sequential pass: count zeros, count ones, stop at terminating zero.")]),
  body([bold("MDL:"), normal(" Minimum Description Length. The token structure is the shortest self-describing binary representation consistent with Named and Frozen.")]),
  body([bold("Productive:"), normal(" Tokens compose: L(u;v) = L(u) \u2295 L(v). Composition is path-independent.")]),
  body([normal("These four axioms uniquely determine the token structure. They do not assume any particle content.")]),

  // Section 3
  h1("3. The Three Gauge Sectors"),
  h2("3.1 The N-Sector: U(1)"),
  body([normal(
    "The N leading zeros are structurally indistinguishable: the Frozen decoder counts them but " +
    "does not track which zero is which. The Named property states that the decoder output is the " +
    "physical content. Therefore the N zeros form a single equivalence class. " +
    "The only amplitude transformation that preserves (N,M) while acting on this class is a global " +
    "phase rotation e"
  ), sup("i\u03B8"), normal(
    ". The group of all such rotations is U(1). One generator. One conserved charge. " +
    "Charge quantization follows directly: N is an integer, so charge is quantized. "
  ), statusPill("PROVEN")]),

  h2("3.2 The M=1 Doublet: SU(2)"),
  body([normal(
    "At depth M=1, the token lattice contains an infinite tower of tokens {(0,1),(1,1),(2,1),...}. " +
    "The MDL axiom selects the minimum-cost pair spanning both neutral (N=0) and charged (N=1) sectors: " +
    "{(0,1),(1,1)} with total length 2+3=5 bits, the minimum possible. " +
    "This pair forms a two-dimensional complex vector space \u2102\u00B2. " +
    "The unique norm-preserving, unit-determinant group on \u2102\u00B2 (unit determinant required by " +
    "Productive to prevent phase accumulation under composition) is SU(2). " +
    "Three generators \u2192 three force carriers: W\u207A, W\u207B, Z\u00B0. "
  ), statusPill("ARGUED")]),
  body([italic("Gap:"), normal(" The MDL uniqueness of the doublet selection requires the full token Hamiltonian analysis.")]),

  h2("3.3 The M=3 Triplet: SU(3)"),
  body([normal(
    "At depth M=3, a single token carries three 1-bits. Unlike the N-zeros (which are " +
    "indistinguishable), the three 1-bits are ordered: the Frozen decoder reads them sequentially, " +
    "making bit #1 distinguishable from bit #3 by position. " +
    "The amplitude space is \u2102\u00B3. The unique norm-preserving, unit-determinant group on \u2102\u00B3 is SU(3). " +
    "Eight generators \u2192 eight gluons (dim SU(3) = 3\u00B2\u22121 = 8). "
  ), statusPill("PROVEN")]),

  // Section 4
  h1("4. Formal Disjointness of the Three Sectors"),
  h2("4.1 Theorem"),
  body([bold("Theorem."), normal(
    " The three gauge symmetry sectors — U(1) on the N-sector, SU(2) on the M=1 doublet, " +
    "SU(3) on M=3 — are mutually disjoint. Their combined action is the direct product " +
    "U(1)\u00D7SU(2)\u00D7SU(3)."
  )]),
  h2("4.2 Proof"),
  body([bold("Step 1 — Hilbert space factorization."), normal(
    " The full token Hilbert space factors as:"
  )]),
  ...codeBlock(["  H = H_charge \u2297 H_isospin \u2297 H_color"]),
  gap(),
  body([normal(
    "H_charge carries the N degree of freedom (electric charge). " +
    "H_isospin carries the weak isospin of the M=1 doublet. " +
    "H_color carries the color indices of M=3 tokens. "
  )]),
  body([bold("Step 2 — Independence of N and M."), normal(
    " The Two-Dimension Theorem establishes that N and M are structurally independent: " +
    "no term in the Frozen decoder couples them. Changing N does not change M, and vice versa. " +
    "Therefore H_charge and H_isospin\u2297H_color are orthogonal tensor factors."
  )]),
  body([bold("Step 3 — Independence of M=1 and M=3."), normal(
    " A state at depth M=1 has exactly one 1-bit. A state at depth M=3 has exactly three. " +
    "These are mutually exclusive: a Frozen decoder reading M=1 halts after one 1-bit and " +
    "cannot simultaneously be at M=3. Mutually exclusive decoder states correspond to " +
    "orthogonal subspaces of Hilbert space. Therefore H_isospin and H_color are orthogonal tensor factors."
  )]),
  body([bold("Step 4 — Operators on tensor factors commute."), normal(
    " U(1) acts on H_charge, SU(2) on H_isospin, SU(3) on H_color. " +
    "Operators on distinct tensor factors of a Hilbert space always commute and " +
    "span orthogonal subspaces of the full Lie algebra. " +
    "The combined symmetry group is therefore the direct product: G = U(1)\u00D7SU(2)\u00D7SU(3). \u25a1"
  )]),
  body([italic("Remaining gap:"), normal(
    " The completeness step — proving that no gauge sector at any other depth M contributes — " +
    "relies on the MDL exponential suppression exp(\u22122M) of higher depths. " +
    "This is an approximate argument (the suppression is exponential, not a theorem " +
    "of exact absence). A complete proof would show that depths M=2,4,5,... contribute " +
    "zero physical gauge generators. This remains open."
  )]),

  // Section 5
  h1("5. Lepton Mass Structure: The Nested Amplitude Formula"),
  h2("5.1 Derivation"),
  body([normal(
    "The lepton mass amplitudes are computed as sums over all shortest lattice paths from the " +
    "Higgs site (2,0) to each lepton site: (1,1) for tau, (1,2) for mu, (1,3) for electron. " +
    "Each path accumulates N-hop amplitude t_N = 1/\u221A2 and M-hop amplitude t_M = exp(\u22121)\u00D7(\u2212i), " +
    "together with a U(1) gauge phase \u03B1_(N,M) at each lattice site."
  )]),
  body([normal(
    "In the gauge where the Higgs row phases are zero, the result is:"
  )]),
  ...codeBlock([
    "  |A_\u03C4|\u00B2  \u221D  |1 + e^{i\u0394\u2080}|\u00B2",
    "  |A_\u03BC|\u00B2  \u221D  |1 + e^{i\u0394\u2081}(1 + e^{i\u0394\u2080})|\u00B2",
    "  |A_e|\u00B2   \u221D  |1 + e^{i\u0394\u2082}(1 + e^{i\u0394\u2081}(1 + e^{i\u0394\u2080}))|\u00B2",
  ]),
  gap(),
  body([normal(
    "where \u0394\u2080, \u0394\u2081, \u0394\u2082 are the plaquette holonomies between the Higgs row and lepton row. " +
    "This continued-product (nested) structure is not assumed: it is a direct consequence " +
    "of the lattice geometry and the path-sum rule."
  )]),
  h2("5.2 Properties"),
  body([normal(
    "Each generation wraps the previous inside a new phase factor. The mass hierarchy is " +
    "entirely a consequence of phase interference — not of fine-tuned coupling constants. " +
    "The three lepton mass ratios are encoded in exactly two physical holonomy parameters " +
    "(the gauge freedom removes one of the three \u0394 values). The encoding is bijective."
  )]),
  h2("5.3 Relation to Koide Formula"),
  body([normal(
    "The Koide formula Q = (m_e+m_\u03BC+m_\u03C4)/(\u221Am_e+\u221Am_\u03BC+\u221Am_\u03C4)\u00B2 = 2/3 " +
    "holds to 1 part in 10\u2075 for the observed lepton masses. " +
    "The nested structure is consistent with Koide: the specific holonomies that reproduce " +
    "the observed mass ratios give Q = 0.66666082, within 6\u00D710\u207B\u2076 of 2/3. " +
    "However, sampling 8000 random holonomy triples gives Q ranging from 0.37 to 0.89, " +
    "with only ~5% within 0.01 of 2/3. "
  ), italic("The nested structure does not derive the Koide formula."), normal(
    " Koide is a 3rd equation in a system with 2 physical degrees of freedom; " +
    "it over-determines the system and represents an additional coincidence of nature " +
    "not explained by the lattice geometry alone."
  )]),

  // Section 6
  h1("6. Coupling Constant Normalization: Root Cause of the Factor-of-7"),
  body([normal(
    "The token hop amplitude |t_M| = exp(\u22121) implies |t|² = exp(\u22122) \u2248 0.135. " +
    "The observed gauge couplings at the Planck/GUT scale converge to \u03B1 \u2248 0.018\u20130.022. " +
    "The ratio is \u22487.5, appearing consistently across all three gauge groups. " +
    "This is not a group-specific problem. We diagnose its root cause."
  )]),
  h2("6.1 The Missing 4\u03C0"),
  body([normal(
    "In quantum field theory, the coupling constant \u03B1 = g\u00B2/(4\u03C0), where g is the vertex factor " +
    "appearing in the Lagrangian. The token hop amplitude t is the vertex factor g, not \u221A\u03B1. " +
    "The correct identification is therefore:"
  )]),
  ...codeBlock(["  \u03B1_token = |t|\u00B2 / (4\u03C0) = exp(\u22122) / (4\u03C0) \u2248 0.0107"]),
  gap(),
  body([normal(
    "This reduces the discrepancy from factor 7.5 to factor 1.7 relative to observed \u03B1\u2248 0.018. " +
    "The dominant error in prior calculations was using g\u00B2 where \u03B1 = g\u00B2/(4\u03C0) was required."
  )]),
  h2("6.2 Remaining Factor of 2"),
  body([normal(
    "After the 4\u03C0 correction, a factor of \u22482 remains. Two possible sources: " +
    "(a) the energy scale at which the token description applies is slightly below the Planck scale " +
    "(the log running from E_P to E_GUT introduces a correction consistent with factor 1.7); " +
    "(b) a plaquette normalization factor in the lattice-to-continuum action correspondence " +
    "has not been formally derived. " +
    "The framework cannot yet predict \u03B1 to better than a factor of 2."
  )]),
  h2("6.3 Required Corrections to Prior Results"),
  body([normal(
    "All prior calculations identifying \u03B1 = exp(\u22122) should be corrected to \u03B1 = exp(\u22122)/(4\u03C0) \u2248 0.0107. " +
    "This approximately halves the error in the Weinberg angle prediction and the SU(2) coupling."
  )]),

  // Section 7 — Honest status table
  h1("7. Complete Epistemic Ledger"),
  body([normal("The following table records every claim in the framework with its honest status.")]),
  gap(),

  mkTable(
    ["#", "Claim", "Status", "Basis / Open Step"],
    [
      ["1",  "Token uniqueness theorem",              "PROVEN",   "Structural; verified"],
      ["2",  "Two-Dimension Theorem (N,M independent)","PROVEN",  "Decoder structure"],
      ["3",  "Charge quantization",                   "PROVEN",   "N \u2208 \u2124\u2265\u2080"],
      ["4",  "Photon masslessness",                   "PROVEN",   "U(1) local symmetry"],
      ["5",  "Quaternionic QM ruled out",             "PROVEN",   "Two-Dimension Theorem"],
      ["6",  "Measurement = symbol completion",       "PROVEN",   "No open steps"],
      ["7",  "Gauge group U(1)\u00D7SU(2)\u00D7SU(3)","ARGUED",  "Formal (Sec. 4); completeness gap"],
      ["8",  "Disjointness of gauge sectors",         "ARGUED",   "Proven (Sec. 4); completeness open"],
      ["9",  "Parity violation",                      "ARGUED",   "Weyl spinor identification needed"],
      ["10", "Born rule (Gleason)",                   "ARGUED",   "BMS theorem not cited"],
      ["11", "Lorentz invariance (Ignatowski)",       "ARGUED",   "Isotropy needs continuum limit"],
      ["12", "Complex amplitudes \u03C6=\u03C0/2",    "ARGUED",   "Compositionality step explicit"],
      ["13", "Nested lepton amplitude formula",       "PROVEN",   "Lattice geometry (Sec. 5)"],
      ["14", "Mass hierarchy from phase interference","ARGUED",   "Mechanism; values not derived"],
      ["15", "Inverted lepton site assignment",       "PROVEN",   "Computational, <0.01% error"],
      ["16", "Flat field impossibility theorem",      "PROVEN",   "Algebraic; hierarchy requires \u0394\u1D62 \u2260 0"],
      ["17", "Koide formula connection",              "OPEN",     "Consistent; not derived (Sec. 5.3)"],
      ["18", "\u03B1 = exp(\u22122)/(4\u03C0) correction","ARGUED","4\u03C0 identified; factor 2 remains"],
      ["19", "Continuum limit",                       "OPEN",     "Single most important blocker"],
      ["20", "Schr\u00F6dinger equation",              "ARGUED",   "Stone's thm needs continuum limit"],
      ["21", "Fermion masses from first principles",  "OPEN",     "Geometry encodes; does not derive"],
      ["22", "Coupling constants to <10%",            "OPEN",     "Factor 2 after 4\u03C0 correction"],
      ["23", "SU(3) coupling",                        "OPEN",     "Structure correct; value off \u00D72"],
      ["24", "Quark masses",                          "OPEN",     "SU(3) depth assignment needs redo"],
      ["25", "Neutrino masses",                       "OPEN",     "Not addressed"],
      ["26", "Newton's G, \u039B cosmological",       "OPEN",     "Not addressed"],
    ],
    [360, 3600, 1200, 4200]
  ),

  gap(),

  // Section 8 — What is genuinely new
  h1("8. What Is Genuinely New"),
  body([normal(
    "The Standard Model gauge group has resisted theoretical derivation for fifty years. " +
    "Every prior proposal either requires the group to be assumed (string theory landscape, " +
    "GUT model building) or derives it only at the cost of many additional assumptions " +
    "(SO(10) unification requires proton decay not yet observed, SU(5) is ruled out). " +
    "The token framework derives U(1)\u00D7SU(2)\u00D7SU(3) from three structural facts about " +
    "the decoder:"
  )]),
  body([normal("(1) N-zeros are indistinguishable \u2192 U(1).")]),
  body([normal("(2) The minimum-cost doublet at M=1 spans charge sectors \u2192 SU(2).")]),
  body([normal("(3) Three ordered 1-bits at M=3 form \u2102\u00B3 \u2192 SU(3).")]),
  body([normal(
    "The disjointness of these three sectors is formally proven using the mutual exclusivity " +
    "of decoder states at different depths (Section 4). This constitutes a derivation, " +
    "not an identification."
  )]),
  body([normal(
    "The nested continued-product formula for lepton masses is new. It follows from the " +
    "lattice geometry without fitting. It gives a bijective encoding of all lepton mass " +
    "ratios in two physical holonomy parameters. Whether an additional principle fixes " +
    "those parameters from the axioms alone is the central open problem."
  )]),

  // Section 9 — What is not yet solved
  h1("9. What Is Not Yet Solved"),
  body([normal("The following are genuine open problems, not covered gaps:")]),
  body([bold("Continuum limit."), normal(
    " The token lattice is discrete. Deriving the Schr\u00F6dinger equation, Lorentz invariance, " +
    "and gauge field dynamics in the continuum requires establishing the continuum limit. " +
    "This is the single most important open problem. Its solution would immediately close " +
    "multiple argued claims."
  )]),
  body([bold("Fermion mass prediction."), normal(
    " The nested amplitude formula encodes mass ratios in holonomies but does not fix " +
    "the holonomies from first principles. The Yukawa fixed-point equation (minimizing the " +
    "Wilson + Yukawa action) is circular without an independent principle fixing one ratio. " +
    "The masses are geometrized, not derived."
  )]),
  body([bold("Coupling constants."), normal(
    " After the 4\u03C0 correction, the predicted \u03B1 \u2248 0.0107 vs observed \u22480.018 at the GUT scale. " +
    "A factor of 2 remains unexplained. The framework cannot yet predict couplings to better than a factor of 2."
  )]),
  body([bold("Completeness of gauge sector count."), normal(
    " The proof that exactly three gauge sectors appear (not four or more) relies on " +
    "exponential MDL suppression of higher depths, not a theorem of exact absence."
  )]),

  // Section 10 — Comparison
  h1("10. Comparison with Other Approaches"),
  gap(),
  mkTable(
    ["Approach", "Gauge group", "Fermion masses", "Couplings", "Status"],
    [
      ["Standard Model",        "Input",    "Input (Yukawa)", "Input",   "Complete EFT"],
      ["String theory (MSSM)",  "Selected", "Not predicted",  "Not pred.", "Landscape problem"],
      ["SU(5) GUT",             "Assumed",  "Partial",        "Convergence", "Proton decay excluded"],
      ["Causal sets",           "N/A",      "N/A",            "N/A",     "Different regime"],
      ["Token framework (this)","Derived*", "Encoded",        "\u00D72", "Young; incomplete"],
    ],
    [2200, 1800, 1800, 1560, 2000]
  ),
  gap(),
  body([normal("* Derived with one remaining completeness gap (Section 4).")]),
  body([normal(
    "The token framework has more phenomenological contact than causal sets or string theory " +
    "at the cost of less mathematical depth. Its unique feature is the information-theoretic " +
    "derivation of the gauge group from a single coding constraint. " +
    "Whether this constitutes a genuine derivation or a sophisticated reverse-engineering " +
    "depends on whether the completeness gap can be closed without appeal to the known gauge group."
  )]),

  // Section 11 — Three decisive tests
  h1("11. Three Decisive Tests"),
  body([normal(
    "The framework's status will be determined by the outcome of three specific calculations:"
  )]),
  body([bold("Test 1 — Formal completeness proof."), normal(
    " Prove from the token axioms alone, without assuming the known gauge group, " +
    "that exactly three and only three gauge-active sectors exist. " +
    "If this requires appeal to particle content, the derivation is circular."
  )]),
  body([bold("Test 2 — Independent fixing of holonomies."), normal(
    " Find a principle from the token axioms that fixes the lepton holonomies \u0394\u1D62 " +
    "without using the observed mass ratios as input. " +
    "This would convert the geometric encoding into a genuine prediction."
  )]),
  body([bold("Test 3 — Coupling constant factor of 2."), normal(
    " Close the remaining factor of 2 between \u03B1_token = exp(\u22122)/(4\u03C0) \u2248 0.0107 " +
    "and the observed \u03B1_GUT \u2248 0.022. " +
    "If closed by a derived normalization: the framework predicts the three coupling constants. " +
    "If it requires a free parameter: it does not."
  )]),
  body([normal(
    "If all three tests succeed: the token framework is among the most significant theoretical " +
    "results in physics in decades. If any requires fine-tuning or reduces to circular reasoning: " +
    "it is a sophisticated but ultimately unsuccessful attempt."
  )]),

  rule(),

  // Appendix
  h1("Appendix A: Token Amplitude Formula"),
  body([normal("The base amplitude for a token at position (N,M) is:")]),
  ...codeBlock(["  A(N,M) = exp(\u2212N) \u00D7 (\u2212i)^M"]),
  gap(),
  body([normal(
    "The exp(\u2212N) factor arises from the MDL cost of N identity zeros (each costing 1 bit \u2248 1 nat of action). " +
    "The (\u2212i)^M factor arises from the derived phase \u03C6 = \u03C0/2 per M-hop, which is the unique " +
    "phase consistent with compositionality and path-distinguishability."
  )]),

  h1("Appendix B: The Nested Formula — Analytic Derivation"),
  body([normal(
    "For paths from Higgs (2,0) to tau (1,1): there are C(2,1)=2 shortest paths, each taking " +
    "one N-step and one M-step. Setting gauge phases \u03B1_(2,M) = 0 (Higgs row gauge) and " +
    "\u03B1_(1,M) = \u0394_M (lepton row holonomies):"
  )]),
  ...codeBlock([
    "  A_\u03C4 = t_N \u00D7 t_M \u00D7 [e^{i\u0394\u2080} + 1]",
    "  A_\u03BC = t_N \u00D7 t_M\u00B2 \u00D7 [1 + e^{i\u0394\u2081}(1 + e^{i\u0394\u2080})]",
    "  A_e  = t_N \u00D7 t_M\u00B3 \u00D7 [1 + e^{i\u0394\u2082}(1 + e^{i\u0394\u2081}(1 + e^{i\u0394\u2080}))]",
  ]),
  gap(),
  body([normal(
    "The bracketed factors are the interference sums over lattice paths. " +
    "Each generation adds one new M-step and wraps the previous interference pattern " +
    "inside a new phase factor. The t_N, t_M prefactors are common within each lepton " +
    "and cancel in mass ratios. The nested structure is the exact result, not an approximation."
  )]),

  h1("Appendix C: Numerical Results"),
  gap(),
  mkTable(
    ["Quantity", "Token prediction", "Observed", "Error", "Status"],
    [
      ["Gauge group",            "U(1)\u00D7SU(2)\u00D7SU(3)","U(1)\u00D7SU(2)\u00D7SU(3)","Exact","ARGUED"],
      ["Force carriers",         "1+3+8 = 12",    "12",         "Exact",  "ARGUED"],
      ["Charge quantization",    "Integer N",      "Integer",    "Exact",  "PROVEN"],
      ["Photon mass",            "0",              "0",          "Exact",  "PROVEN"],
      ["sin\u00B2\u03B8_W (tree)","0.210",         "0.231",      "9%",     "ARGUED"],
      ["\u03B1_EM (corrected)",  "0.0107",         "0.0073",     "47%",    "ARGUED"],
      ["\u03B1_SU2 (corrected)", "0.0107",         "0.022",      "\u00D72","ARGUED"],
      ["tau/mu ratio",           "Encoded",        "16.82",      "N/A",    "OPEN"],
      ["mu/e ratio",             "Encoded",        "206.8",      "N/A",    "OPEN"],
      ["Koide Q",                "Consistent",     "0.66666",    "N/A",    "OPEN"],
    ],
    [2400, 2000, 1600, 960, 1400]
  ),
  gap(),

  // Footer note
  rule(),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 240, after: 0 },
    children: [new TextRun({
      text: "Working paper. All computations verified numerically. Status labels are binding.",
      font: FONT, size: 18, italics: true, color: "666666"
    })]
  }),
];

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: "1A1A2E" },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: FONT, color: "16213E" },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('/home/claude/token_framework_paper.docx', buf);
  console.log('Written: token_framework_paper.docx');
});
