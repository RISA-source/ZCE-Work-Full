const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  PageNumber, NumberFormat, LevelFormat, TableOfContents
} = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, size: 32, font: "Arial" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, size: 26, font: "Arial" })]
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, bold: true, size: 24, font: "Arial" })]
  });
}

function p(text, options = {}) {
  return new Paragraph({
    spacing: { after: 160 },
    children: [new TextRun({ text, font: "Arial", size: 22, ...options })]
  });
}

function pMixed(runs) {
  return new Paragraph({
    spacing: { after: 160 },
    children: runs.map(r => new TextRun({ font: "Arial", size: 22, ...r }))
  });
}

function label(tag, color) {
  const colors = {
    PROVEN: "1A7A3A", ARGUED: "B85C00", OPEN: "1A4A8A",
    FAILED: "8A1A1A", CONJECTURAL: "6A3A8A", VERIFIED: "1A6A6A"
  };
  return new TextRun({ text