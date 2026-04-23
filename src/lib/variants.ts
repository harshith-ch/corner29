export type VariantDef = {
  slug: string;
  label: string;
  hint: string;
  style: 'architectural' | 'boutique' | 'editorial';
};

export const variants: VariantDef[] = [
  {
    slug: 'architectural',
    label: 'Architectural',
    hint: 'Swiss grid · mono',
    style: 'architectural'
  },
  {
    slug: 'boutique',
    label: 'Boutique',
    hint: 'Warm · rounded',
    style: 'boutique'
  },
  {
    slug: 'editorial',
    label: 'Editorial',
    hint: 'Serif · measured',
    style: 'editorial'
  }
];
