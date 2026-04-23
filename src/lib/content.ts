export type Stat = { value: string; label: string };

export type FloorKey = 'B3' | 'B2' | 'B1' | 'G' | '1' | '2' | '3' | '4';

export type Floor = {
  key: FloorKey;
  title: string;
  svg: string;
  summary?: string;
  rooms?: string[];
};

export type Listing = {
  title: string;
  pitch: string;
  location: {
    label: string;
    address: string;
    plusCode: string;
    mapsEmbedSrc: string;
    directionsUrl: string;
  };
  stats: Stat[];
  common: string[];
  floors: Floor[];
  parking: string[];
};

export const listing: Listing = {
  title: 'G+4 Standalone Office for Lease',
  pitch:
    'A ready-to-occupy plug-and-play office on Kondapur Main Road — 600 seats, 50+ cabins & meeting rooms, a 5,000 sft rooftop cafeteria, and 3 levels of parking with a car lift.',
  location: {
    label: 'Kondapur Main Road, Hyderabad',
    address: 'Serilingampalle (M), Telangana',
    plusCode: 'F979+V3 Serilingampalle (M), Telangana',
    mapsEmbedSrc:
      'https://www.google.com/maps?q=F979%2BV3%20Serilingampalle%20Telangana&output=embed',
    directionsUrl:
      'https://www.google.com/maps/dir/?api=1&destination=F979%2BV3%20Serilingampalle%20Telangana'
  },
  stats: [
    { value: '600', label: 'Plug & Play Seats' },
    { value: '50+', label: 'Rooms & Cabins' },
    { value: '5,000 sft', label: 'AC Rooftop Cafeteria' },
    { value: '3 Levels', label: 'Parking + Car Lift' }
  ],
  common: [
    'Pantry',
    'Restrooms',
    '2 × passenger elevators',
    '2 × stairways',
    '2 × lift / stair lobbies (~120 sft each)'
  ],
  floors: [
    {
      key: 'B3',
      title: 'Basement 3',
      svg: '/svg/basement_floor_3.svg',
      summary: 'Parking level',
      rooms: ['Car + bike parking', 'Equipment + store']
    },
    {
      key: 'B2',
      title: 'Basement 2',
      svg: '/svg/basement_floor_2.svg',
      summary: 'Parking level',
      rooms: ['Car + bike parking']
    },
    {
      key: 'B1',
      title: 'Stilt / Basement 1',
      svg: '/svg/stilt_floor_plan.svg',
      summary: 'Parking + car lift',
      rooms: ['45 car parking', 'Bike parking', '1 car lift']
    },
    {
      key: 'G',
      title: 'Ground Floor',
      svg: '/svg/ground_floor.svg',
      summary: '26 cubicles · 19 open seats · 13 meeting rooms',
      rooms: [
        'Lobby (~300 sft)',
        'Cubicle seating × 26',
        'Open row seating × 19',
        'Training room (775 sft)',
        'Board room (540 sft)',
        '3-person rooms × 6',
        '6-person rooms × 4',
        '12-person room × 1'
      ]
    },
    {
      key: '1',
      title: '1st Floor',
      svg: '/svg/first_floor.svg',
      summary: '132 open seats · 10 meeting rooms',
      rooms: [
        'Open row seating × 132',
        '20-person room × 1',
        '12-person rooms × 3',
        '6-person rooms × 5',
        '3-person room × 1'
      ]
    },
    {
      key: '2',
      title: '2nd Floor',
      svg: '/svg/second_floor.svg',
      summary: '135 open seats · 10 meeting rooms',
      rooms: [
        'Open row seating × 135',
        '20-person rooms × 3',
        '12-person rooms × 7'
      ]
    },
    {
      key: '3',
      title: '3rd Floor',
      svg: '/svg/third_floor.svg',
      summary: '145 open seats · 9 meeting rooms',
      rooms: [
        'Open row seating × 145',
        '20-person rooms × 3',
        '6-person rooms × 5',
        '3-person room × 1'
      ]
    },
    {
      key: '4',
      title: '4th Floor',
      svg: '/svg/fourth_floor.svg',
      summary: '132 open seats · 10 meeting rooms',
      rooms: [
        'Open row seating × 132',
        '20-person rooms × 4',
        '12-person rooms × 5',
        '3-person room × 1'
      ]
    }
  ],
  parking: [
    '3 levels of parking',
    '45 car parking spaces',
    '1 car lift',
    'Dedicated bike parking',
    'Equipment + store rooms'
  ]
};
