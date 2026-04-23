export type VariantDef = {
  slug: string;
  label: string;
  hint: string;
  layout: 'single' | 'tabs';
  style: 'architectural' | 'boutique' | 'editorial';
};

export const variants: VariantDef[] = [
  {
    slug: 'architectural',
    label: 'Architectural',
    hint: 'Swiss grid · single page',
    layout: 'single',
    style: 'architectural'
  },
  {
    slug: 'boutique',
    label: 'Boutique',
    hint: 'Warm · single page',
    layout: 'single',
    style: 'boutique'
  },
  {
    slug: 'boutique-tabs',
    label: 'Boutique (top-bar)',
    hint: 'Warm · tabbed sections',
    layout: 'tabs',
    style: 'boutique'
  },
  {
    slug: 'editorial',
    label: 'Editorial',
    hint: 'Serif · single page',
    layout: 'single',
    style: 'editorial'
  },
  {
    slug: 'editorial-tabs',
    label: 'Editorial (top-bar)',
    hint: 'Serif · tabbed sections',
    layout: 'tabs',
    style: 'editorial'
  }
];
