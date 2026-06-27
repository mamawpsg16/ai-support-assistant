// catalog.js — front-end-only presentation metadata for products.
//
// The design's product cards show a category label and a coloured tile with the
// product's initials. Our backend Product table has no `category` column and no art,
// so we derive those here on the client. (When a category column is added to the
// backend later, swap categoryFor() to read product.category instead.)

// Map known product names -> category. Mirrors the design's catalog. Anything we don't
// recognise falls back to "Other", so new products still render fine.
const CATEGORY_BY_NAME = {
  'Wireless Mouse': 'Peripherals',
  'Mechanical Keyboard': 'Peripherals',
  'USB-C Hub': 'Connectivity',
  '1080p Webcam': 'Video',
  'Laptop Stand': 'Ergonomics',
  'Desk Lamp': 'Lighting',
  'Mousepad XL': 'Ergonomics',
  'Monitor Arm': 'Mounts',
}

// Preferred chip order (only categories actually present get shown — see StoreView).
export const CATEGORY_ORDER = [
  'Peripherals',
  'Connectivity',
  'Video',
  'Ergonomics',
  'Lighting',
  'Mounts',
  'Other',
]

export function categoryFor(product) {
  return CATEGORY_BY_NAME[product.name] || 'Other'
}

// Tile colour per category (the design's tints). Keeps a product's tile stable.
const TILE_BY_CATEGORY = {
  Peripherals: { bg: '#EEF5F1', col: '#4A7A58' },
  Connectivity: { bg: '#EDF2F7', col: '#3D6A8A' },
  Video: { bg: '#FDF4E8', col: '#C07830' },
  Ergonomics: { bg: '#EEF5F1', col: '#4A7A58' },
  Lighting: { bg: '#FDF4E8', col: '#C07830' },
  Mounts: { bg: '#EEF5F1', col: '#4A7A58' },
  Other: { bg: '#F2F0EC', col: '#6A6860' },
}

// Up to two initials from the product name: "Wireless Mouse" -> "WM", "USB-C Hub" -> "UH".
function initials(name) {
  return (name || '?')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase()
}

// Everything a card needs to draw the tile: background, letter colour, the initials.
export function tileFor(product) {
  const cat = categoryFor(product)
  return { ...(TILE_BY_CATEGORY[cat] || TILE_BY_CATEGORY.Other), ab: initials(product.name) }
}
