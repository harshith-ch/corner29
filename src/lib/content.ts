export type Stat = { value: string; label: string };

export type FloorKey = 'B3' | 'B2' | 'B1' | 'G' | '1' | '2' | '3' | '4';

export type Camera = {
  id: string;
  x: number;
  y: number;
  heading: number;
  fov?: number;
  image: string;
  title?: string;
  caption?: string;
};

export type Floor = {
  key: FloorKey;
  title: string;
  svg: string;
  summary?: string;
  rooms?: string[];
  cameras?: Camera[];
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
      rooms: ['Car + bike parking', 'Equipment + store'],
      cameras: [
        {
          id: 'b3-cam-1',
          x: 4594338.5,
          y: 547458.69,
          heading: 314,
          image: '/pics/b3/DSC03715.jpg',
          title: 'b3',
          caption: 'B3'
        }
      ]
    },
    {
      key: 'B2',
      title: 'Basement 2',
      svg: '/svg/basement_floor_2.svg',
      summary: 'Parking level',
      rooms: ['Car + bike parking'],
      cameras: [
        {
          id: 'b2-cam-1',
          x: 4668272.0,
          y: 548081.5,
          heading: 314,
          image: '/pics/b2/DSC03705.jpg',
          title: 'b2',
          caption: 'B2'
        }
      ]
    },
    {
      key: 'B1',
      title: 'Stilt / Basement 1',
      svg: '/svg/stilt_floor_plan.svg',
      summary: 'Parking + car lift',
      rooms: ['45 car parking', 'Bike parking', '1 car lift'],
      cameras: [
        {
          id: 'b1-cam-1',
          x: 4724967.0,
          y: 540479.56,
          heading: 88,
          image: '/pics/b1/DSC03700.jpg',
          title: 'back-entrace',
          caption: 'back-entrance'
        },
        {
          id: 'b1-cam-2',
          x: 4747688.0,
          y: 540068.44,
          heading: 87,
          image: '/pics/b1/DSC03703.jpg',
          title: 'car-lift',
          caption: 'Car Lift'
        }
      ]
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
      ],
      cameras: [
        {
          id: 'g-cam-1',
          x: 13495.96,
          y: -14195.46,
          heading: 90,
          image: '/pics/ground/DSC03509.jpg',
          title: 'seating-1',
          caption: 'Seating alley 1'
        },
        {
          id: 'g-cam-2',
          x: 20008.01,
          y: -14260.93,
          heading: 319,
          image: '/pics/ground/DSC03510.jpg',
          title: 'seating-2',
          caption: 'Open Seating'
        },
        {
          id: 'g-cam-3',
          x: 24432.84,
          y: -14584.36,
          heading: 241,
          image: '/pics/ground/DSC03511.jpg',
          title: 'cubicles',
          caption: 'Cubicle Seats'
        },
        {
          id: 'g-cam-4',
          x: 29136.36,
          y: -13847.63,
          heading: 317,
          image: '/pics/ground/DSC03512.jpg',
          title: 'alley-and-meeting-rooms',
          caption: 'Passage and meeting rooms'
        },
        {
          id: 'g-cam-5',
          x: 30113.19,
          y: -20602.02,
          heading: 48,
          image: '/pics/ground/DSC03496.jpg',
          title: 'md-room',
          caption: 'MD Room'
        },
        {
          id: 'g-cam-6',
          x: 27331.72,
          y: -18975.12,
          heading: 311,
          image: '/pics/ground/DSC03486.jpg',
          title: 'conference-room',
          caption: 'Conference Room'
        },
        {
          id: 'g-cam-7',
          x: 3617.41,
          y: -9305.93,
          heading: 91,
          image: '/pics/ground/DSC03507.jpg',
          title: 'training-room',
          caption: 'Training Room'
        },
        {
          id: 'g-cam-8',
          x: 29790.04,
          y: -17354.05,
          heading: 51,
          image: '/pics/ground/DSC03479.jpg',
          title: 'meeting-room',
          caption: 'Meeting Room'
        },
        {
          id: 'g-cam-9',
          x: 34326.95,
          y: -11875.78,
          heading: 319,
          image: '/pics/ground/DSC03519.jpg',
          title: 'lobby',
          caption: 'Lobby'
        }
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
      ],
      cameras: [
        {
          id: '1-cam-1',
          x: 57613.64,
          y: -14971.17,
          heading: 90,
          image: '/pics/first/DSC03569.jpg',
          title: 'seating-1',
          caption: 'Open Seating'
        },
        {
          id: '1-cam-2',
          x: 75892.93,
          y: -20024.37,
          heading: 268,
          image: '/pics/first/DSC03561.jpg',
          title: 'seating-2',
          caption: 'Open Seating'
        },
        {
          id: '1-cam-3',
          x: 55213.87,
          y: -9739.75,
          heading: 226,
          image: '/pics/first/DSC03565.jpg',
          title: 'telephone-booth',
          caption: 'Telephone Booth Area'
        },
        {
          id: '1-cam-4',
          x: 76523.66,
          y: -6676.92,
          heading: 268,
          image: '/pics/first/DSC03548.jpg',
          title: 'lift-lobby',
          caption: 'Lift Lobby'
        },
        {
          id: '1-cam-5',
          x: 72336.88,
          y: -10858.73,
          heading: 221,
          image: '/pics/first/DSC03558.jpg',
          title: 'meeting-room',
          caption: 'Meeting Room'
        }
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
