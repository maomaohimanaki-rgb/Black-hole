// GERADO por tools/build_storyboard_data.py a partir de spec/. NÃO EDITE À MÃO.
export const DATA = {
 "meta": {
  "filmTicks": 720,
  "outroTicks": 20,
  "tickRate": 20
 },
 "acts": [
  {
   "id": "I",
   "name": "ANOMALIA",
   "ticks": [
    0,
    79
   ]
  },
  {
   "id": "II",
   "name": "INSPIRAL",
   "ticks": [
    80,
    239
   ]
  },
  {
   "id": "III",
   "name": "FUSÃO",
   "ticks": [
    240,
    279
   ]
  },
  {
   "id": "IV",
   "name": "DISCO",
   "ticks": [
    280,
    419
   ]
  },
  {
   "id": "V",
   "name": "O PUXÃO",
   "ticks": [
    420,
    539
   ]
  },
  {
   "id": "VI",
   "name": "HORIZONTE",
   "ticks": [
    540,
    619
   ]
  },
  {
   "id": "VII",
   "name": "EVAPORAÇÃO",
   "ticks": [
    620,
    719
   ]
  }
 ],
 "blocks": [
  {
   "id": "B01",
   "act": "I",
   "name": "O SILÊNCIO ERRADO",
   "ticks": [
    0,
    19
   ],
   "camera": [
    {
     "t": 0,
     "pos": {
      "rel": "G",
      "f": -35.0,
      "r": 0.0,
      "u": 0.6
     },
     "look": {
      "rel": "G",
      "f": 0.0,
      "r": 0.0,
      "u": 10.5
     },
     "ease": "linear",
     "fov": 50
    },
    {
     "t": 19,
     "pos": {
      "rel": "G",
      "f": -28.0,
      "r": 0.0,
      "u": 0.6
     },
     "look": {
      "rel": "G",
      "f": 0.0,
      "r": 0.0,
      "u": 21.0
     },
     "ease": "inOutSine",
     "fov": 48
    }
   ],
   "hud": [
    {
     "t": 4,
     "ch": "SB",
     "clear": 30,
     "key": "sgx.hud.b01.0"
    },
    {
     "t": 8,
     "ch": "HD",
     "clear": 19,
     "key": "sgx.hud.b01.1"
    }
   ],
   "flash": [],
   "shake": [
    {
     "t": 12,
     "level": 1
    }
   ],
   "vfx": [
    {
     "t": 0,
     "fx": "dust_inflow"
    },
    {
     "t": 12,
     "fx": "grass_lean"
    }
   ],
   "destruction": []
  },
  {
   "id": "B02",
   "act": "I",
   "name": "O PONTO",
   "ticks": [
    20,
    39
   ],
   "camera": [
    {
     "t": 20,
     "pos": {
      "rel": "G",
      "f": -28.0,
      "r": 0.0,
      "u": 0.6
     },
     "look": "O",
     "ease": "linear",
     "fov": 48
    },
    {
     "t": 39,
     "pos": {
      "rel": "G",
      "f": -49.0,
      "r": 10.5,
      "u": 21.0
     },
     "look": "O",
     "ease": "outCubic",
     "fov": 42
    }
   ],
   "hud": [
    {
     "t": 20,
     "ch": "SB",
     "clear": 39,
     "key": "sgx.hud.b02.0"
    },
    {
     "t": 22,
     "ch": "HD",
     "clear": 39,
     "key": "sgx.hud.b02.1"
    }
   ],
   "flash": [
    {
     "t": 20,
     "level": "N2",
     "kind": "negative_micro",
     "color": 4,
     "dur": null
    }
   ],
   "shake": [
    {
     "t": 20,
     "level": 2
    },
    {
     "t": 24,
     "level": 1
    }
   ],
   "vfx": [
    {
     "t": 20,
     "fx": "bh_spawn"
    },
    {
     "t": 24,
     "fx": "lens_glint"
    },
    {
     "t": 28,
     "fx": "lens_glint"
    },
    {
     "t": 32,
     "fx": "lens_glint"
    },
    {
     "t": 20,
     "fx": "dust_inflow"
    },
    {
     "t": 26,
     "fx": "bh_grow"
    }
   ],
   "destruction": []
  },
  {
   "id": "B03",
   "act": "I",
   "name": "O GÊMEO",
   "ticks": [
    40,
    59
   ],
   "camera": [
    {
     "t": 40,
     "pos": {
      "rel": "G",
      "f": -49.0,
      "r": 10.5,
      "u": 21.0
     },
     "look": "O",
     "ease": "linear",
     "fov": 42
    },
    {
     "t": 42,
     "pos": {
      "rel": "G",
      "f": -49.0,
      "r": 10.5,
      "u": 21.0
     },
     "look": "B",
     "ease": "outExpo",
     "fov": 50
    },
    {
     "t": 59,
     "pos": {
      "around": "O",
      "r": 56.0,
      "az": 20,
      "el": 15
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 55
    }
   ],
   "hud": [
    {
     "t": 40,
     "ch": "HD",
     "clear": 59,
     "key": "sgx.hud.b03.0"
    },
    {
     "t": 50,
     "ch": "SB",
     "clear": 79,
     "key": "sgx.hud.b03.1"
    }
   ],
   "flash": [
    {
     "t": 40,
     "level": "N2",
     "kind": "negative_micro",
     "color": 4,
     "dur": null
    }
   ],
   "shake": [
    {
     "t": 40,
     "level": 2
    }
   ],
   "vfx": [
    {
     "t": 40,
     "fx": "bh_spawn"
    },
    {
     "t": 46,
     "fx": "bh_grow"
    },
    {
     "t": 48,
     "fx": "binary_orbit_start"
    },
    {
     "t": 50,
     "fx": "dust_spiral"
    }
   ],
   "destruction": []
  },
  {
   "id": "B04",
   "act": "I",
   "name": "A DANÇA COMEÇA",
   "ticks": [
    60,
    79
   ],
   "camera": [
    {
     "t": 60,
     "pos": {
      "around": "O",
      "r": 56.0,
      "az": 20,
      "el": 15
     },
     "look": "O",
     "ease": "linear",
     "fov": 55
    },
    {
     "t": 79,
     "pos": {
      "around": "O",
      "r": 77.0,
      "az": 40,
      "el": 50
     },
     "look": "O",
     "ease": "inOutCubic",
     "fov": 60
    }
   ],
   "hud": [
    {
     "t": 60,
     "ch": "HD",
     "clear": 79,
     "key": "sgx.hud.b04.0"
    }
   ],
   "flash": [],
   "shake": [
    {
     "t": 60,
     "level": 1
    }
   ],
   "vfx": [
    {
     "t": 74,
     "fx": "ground_ripple"
    }
   ],
   "destruction": []
  },
  {
   "id": "B05",
   "act": "II",
   "name": "ESPIRAL",
   "ticks": [
    80,
    139
   ],
   "camera": [
    {
     "t": 80,
     "pos": {
      "around": "O",
      "r": 77.0,
      "az": 40,
      "el": 50
     },
     "look": "O",
     "ease": "linear",
     "fov": 60
    },
    {
     "t": 139,
     "pos": {
      "around": "O",
      "r": 56.0,
      "az": -60,
      "el": 25
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 58
    }
   ],
   "hud": [
    {
     "t": 80,
     "ch": "HD",
     "clear": 99,
     "key": "sgx.hud.b05.0"
    },
    {
     "t": 100,
     "ch": "HD",
     "clear": 119,
     "key": "sgx.hud.b05.1"
    },
    {
     "t": 120,
     "ch": "HD",
     "clear": 139,
     "key": "sgx.hud.b05.2"
    }
   ],
   "flash": [],
   "shake": [
    {
     "t": 80,
     "level": 1
    },
    {
     "t": 120,
     "level": 2
    }
   ],
   "vfx": [
    {
     "t": 87,
     "fx": "ground_ripple"
    },
    {
     "t": 99,
     "fx": "ground_ripple"
    },
    {
     "t": 112,
     "fx": "ground_ripple"
    },
    {
     "t": 124,
     "fx": "ground_ripple"
    },
    {
     "t": 135,
     "fx": "ground_ripple"
    },
    {
     "t": 80,
     "fx": "mini_disks"
    },
    {
     "t": 90,
     "fx": "leaf_vortex"
    }
   ],
   "destruction": []
  },
  {
   "id": "B06",
   "act": "II",
   "name": "ACELERAÇÃO",
   "ticks": [
    140,
    199
   ],
   "camera": [
    {
     "t": 140,
     "pos": {
      "around": "O",
      "r": 56.0,
      "az": -60,
      "el": 25
     },
     "look": "O",
     "ease": "linear",
     "fov": 58
    },
    {
     "t": 199,
     "pos": {
      "around": "O",
      "r": 42.0,
      "az": -170,
      "el": 6
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 66,
     "handheld": 0.15
    }
   ],
   "hud": [
    {
     "t": 140,
     "ch": "HD",
     "clear": 169,
     "key": "sgx.hud.b06.0"
    },
    {
     "t": 170,
     "ch": "HD",
     "clear": 199,
     "key": "sgx.hud.b06.1"
    }
   ],
   "flash": [],
   "shake": [
    {
     "t": 140,
     "level": 2
    },
    {
     "t": 180,
     "level": 3
    }
   ],
   "vfx": [
    {
     "t": 146,
     "fx": "ground_ripple"
    },
    {
     "t": 156,
     "fx": "ground_ripple"
    },
    {
     "t": 166,
     "fx": "ground_ripple"
    },
    {
     "t": 176,
     "fx": "ground_ripple"
    },
    {
     "t": 185,
     "fx": "ground_ripple"
    },
    {
     "t": 194,
     "fx": "ground_ripple"
    },
    {
     "t": 150,
     "fx": "eclipse_glints"
    },
    {
     "t": 160,
     "fx": "dust_spiral"
    }
   ],
   "destruction": []
  },
  {
   "id": "B07",
   "act": "II",
   "name": "O GRITO",
   "ticks": [
    200,
    239
   ],
   "camera": [
    {
     "t": 200,
     "pos": {
      "around": "O",
      "r": 42.0,
      "az": -170,
      "el": 6
     },
     "look": "O",
     "ease": "linear",
     "fov": 66
    },
    {
     "t": 202,
     "pos": {
      "around": "O",
      "r": 42.0,
      "az": -170,
      "el": 6
     },
     "look": "O",
     "ease": "step",
     "fov": 63,
     "cut": true
    },
    {
     "t": 209,
     "pos": {
      "around": "O",
      "r": 38.85,
      "az": -174,
      "el": 6
     },
     "look": "O",
     "ease": "step",
     "fov": 60,
     "cut": true
    },
    {
     "t": 216,
     "pos": {
      "around": "O",
      "r": 36.05,
      "az": -178,
      "el": 6
     },
     "look": "O",
     "ease": "step",
     "fov": 57,
     "cut": true
    },
    {
     "t": 222,
     "pos": {
      "around": "O",
      "r": 32.9,
      "az": -182,
      "el": 6
     },
     "look": "O",
     "ease": "step",
     "fov": 54,
     "cut": true
    },
    {
     "t": 227,
     "pos": {
      "around": "O",
      "r": 30.1,
      "az": -186,
      "el": 6
     },
     "look": "O",
     "ease": "step",
     "fov": 51,
     "cut": true
    },
    {
     "t": 232,
     "pos": {
      "around": "O",
      "r": 26.95,
      "az": -190,
      "el": 6
     },
     "look": "O",
     "ease": "step",
     "fov": 48,
     "cut": true
    },
    {
     "t": 236,
     "pos": {
      "around": "O",
      "r": 24.15,
      "az": -194,
      "el": 6
     },
     "look": "O",
     "ease": "step",
     "fov": 45,
     "cut": true
    },
    {
     "t": 239,
     "pos": {
      "around": "O",
      "r": 21.0,
      "az": -198,
      "el": 6
     },
     "look": "O",
     "ease": "step",
     "fov": 42,
     "cut": true
    }
   ],
   "hud": [
    {
     "t": 200,
     "ch": "HD",
     "clear": 229,
     "key": "sgx.hud.b07.0"
    },
    {
     "t": 230,
     "ch": "HD",
     "clear": 235,
     "key": "sgx.hud.b07.1"
    },
    {
     "t": 236,
     "ch": "HD",
     "clear": 238,
     "key": "sgx.hud.b07.2"
    },
    {
     "t": 239,
     "ch": "HD",
     "clear": 240,
     "key": "sgx.hud.b07.3"
    }
   ],
   "flash": [
    {
     "t": 202,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 209,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 216,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 222,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 227,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 232,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 236,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 239,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    }
   ],
   "shake": [
    {
     "t": 200,
     "level": 3
    },
    {
     "t": 222,
     "level": 4
    },
    {
     "t": 232,
     "level": 5
    },
    {
     "t": 236,
     "level": 6
    }
   ],
   "vfx": [
    {
     "t": 202,
     "fx": "ground_ripple"
    },
    {
     "t": 209,
     "fx": "ground_ripple"
    },
    {
     "t": 216,
     "fx": "ground_ripple"
    },
    {
     "t": 222,
     "fx": "ground_ripple"
    },
    {
     "t": 227,
     "fx": "ground_ripple"
    },
    {
     "t": 232,
     "fx": "ground_ripple"
    },
    {
     "t": 236,
     "fx": "ground_ripple"
    },
    {
     "t": 220,
     "fx": "photon_rings_merge"
    },
    {
     "t": 230,
     "fx": "dust_sheet"
    }
   ],
   "destruction": []
  },
  {
   "id": "B08",
   "act": "III",
   "name": "FUSÃO / RINGDOWN",
   "ticks": [
    240,
    259
   ],
   "camera": [
    {
     "t": 240,
     "pos": {
      "around": "O",
      "r": 21.0,
      "az": -198,
      "el": 6
     },
     "look": "O",
     "ease": "step",
     "fov": 40,
     "impact_frame": 2
    },
    {
     "t": 242,
     "pos": {
      "around": "O",
      "r": 140.0,
      "az": -200,
      "el": 12
     },
     "look": "O",
     "ease": "step",
     "fov": 70,
     "cut": true
    },
    {
     "t": 247,
     "pos": {
      "around": "O",
      "r": 140.0,
      "az": -200,
      "el": 12
     },
     "look": "O",
     "ease": "outSine",
     "fov": 76
    },
    {
     "t": 250,
     "pos": {
      "around": "O",
      "r": 140.0,
      "az": -200,
      "el": 12
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 66
    },
    {
     "t": 253,
     "pos": {
      "around": "O",
      "r": 140.0,
      "az": -200,
      "el": 12
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 73
    },
    {
     "t": 256,
     "pos": {
      "around": "O",
      "r": 140.0,
      "az": -200,
      "el": 12
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 68
    },
    {
     "t": 259,
     "pos": {
      "around": "O",
      "r": 136.5,
      "az": -200,
      "el": 12
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 70
    }
   ],
   "hud": [
    {
     "t": 241,
     "ch": "SB",
     "clear": 262,
     "key": "sgx.hud.b08.0"
    },
    {
     "t": 241,
     "ch": "HD",
     "clear": 245,
     "key": "sgx.hud.b08.1"
    },
    {
     "t": 246,
     "ch": "HD",
     "clear": 262,
     "key": "sgx.hud.b08.2"
    }
   ],
   "flash": [
    {
     "t": 240,
     "level": "N4",
     "kind": "impact_negative",
     "color": 0,
     "dur": 2
    },
    {
     "t": 242,
     "level": "N3",
     "kind": "white",
     "color": 0,
     "dur": null
    }
   ],
   "shake": [
    {
     "t": 241,
     "level": 10
    },
    {
     "t": 247,
     "level": 6
    },
    {
     "t": 250,
     "level": 3
    }
   ],
   "vfx": [
    {
     "t": 240,
     "fx": "merge"
    },
    {
     "t": 241,
     "fx": "ringdown_wobble"
    },
    {
     "t": 241,
     "fx": "gw_shell"
    },
    {
     "t": 241,
     "fx": "leaf_burst"
    }
   ],
   "destruction": []
  },
  {
   "id": "B09",
   "act": "III",
   "name": "O VAZIO RESPIRA",
   "ticks": [
    260,
    279
   ],
   "camera": [
    {
     "t": 260,
     "pos": {
      "around": "O",
      "r": 136.5,
      "az": -200,
      "el": 12
     },
     "look": "O",
     "ease": "linear",
     "fov": 70
    },
    {
     "t": 279,
     "pos": {
      "around": "O",
      "r": 91.0,
      "az": -205,
      "el": 8
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 64
    }
   ],
   "hud": [],
   "flash": [],
   "shake": [],
   "vfx": [
    {
     "t": 260,
     "fx": "dust_settle"
    },
    {
     "t": 272,
     "fx": "first_sparks"
    }
   ],
   "destruction": []
  },
  {
   "id": "B10",
   "act": "IV",
   "name": "IGNIÇÃO DO DISCO",
   "ticks": [
    280,
    309
   ],
   "camera": [
    {
     "t": 280,
     "pos": {
      "around": "O",
      "r": 91.0,
      "az": -205,
      "el": 8
     },
     "look": "O",
     "ease": "linear",
     "fov": 64
    },
    {
     "t": 309,
     "pos": {
      "around": "O",
      "r": 70.0,
      "az": -145,
      "el": 12
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 60
    }
   ],
   "hud": [
    {
     "t": 280,
     "ch": "SB",
     "clear": 309,
     "key": "sgx.hud.b10.0"
    },
    {
     "t": 300,
     "ch": "HD",
     "clear": 330,
     "key": "sgx.hud.b10.1"
    }
   ],
   "flash": [
    {
     "t": 304,
     "level": "N3",
     "kind": "white",
     "color": 5,
     "dur": null
    }
   ],
   "shake": [
    {
     "t": 280,
     "level": 2
    },
    {
     "t": 292,
     "level": 3
    },
    {
     "t": 304,
     "level": 4
    }
   ],
   "vfx": [
    {
     "t": 280,
     "fx": "matter_streams"
    },
    {
     "t": 280,
     "fx": "disk_ring_ignite"
    },
    {
     "t": 286,
     "fx": "disk_ring_ignite"
    },
    {
     "t": 292,
     "fx": "disk_ring_ignite"
    },
    {
     "t": 298,
     "fx": "disk_ring_ignite"
    },
    {
     "t": 304,
     "fx": "disk_ring_ignite"
    }
   ],
   "destruction": []
  },
  {
   "id": "B11",
   "act": "IV",
   "name": "O ANEL",
   "ticks": [
    310,
    349
   ],
   "camera": [
    {
     "t": 310,
     "pos": {
      "around": "O",
      "r": 70.0,
      "az": -145,
      "el": 12
     },
     "look": "O",
     "ease": "linear",
     "fov": 60
    },
    {
     "t": 349,
     "pos": {
      "around": "O",
      "r": 49.0,
      "az": -135,
      "el": 9
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 52
    }
   ],
   "hud": [
    {
     "t": 315,
     "ch": "HD",
     "clear": 329,
     "key": "sgx.hud.b11.0"
    },
    {
     "t": 330,
     "ch": "HD",
     "clear": 349,
     "key": "sgx.hud.b11.1"
    }
   ],
   "flash": [],
   "shake": [],
   "vfx": [
    {
     "t": 310,
     "fx": "impostor_hero"
    },
    {
     "t": 310,
     "fx": "lensed_starfield"
    },
    {
     "t": 310,
     "fx": "disk_turbulence"
    }
   ],
   "destruction": []
  },
  {
   "id": "B12",
   "act": "IV",
   "name": "JATOS",
   "ticks": [
    350,
    389
   ],
   "camera": [
    {
     "t": 350,
     "pos": {
      "around": "O",
      "r": 49.0,
      "az": -135,
      "el": 9
     },
     "look": "O",
     "ease": "linear",
     "fov": 52
    },
    {
     "t": 360,
     "pos": {
      "around": "O",
      "r": 105.0,
      "az": -120,
      "el": -10
     },
     "look": {
      "pitch": -35,
      "yaw_rel": 0
     },
     "ease": "step",
     "fov": 70,
     "cut": true
    },
    {
     "t": 380,
     "pos": {
      "around": "O",
      "r": 105.0,
      "az": -120,
      "el": -10
     },
     "look": {
      "pitch": -80,
      "yaw_rel": 0
     },
     "ease": "inOutCubic",
     "fov": 74
    },
    {
     "t": 389,
     "pos": {
      "around": "O",
      "r": 91.0,
      "az": -110,
      "el": 4
     },
     "look": "G",
     "ease": "inOutSine",
     "fov": 70
    }
   ],
   "hud": [
    {
     "t": 362,
     "ch": "SB",
     "clear": 389,
     "key": "sgx.hud.b12.0"
    },
    {
     "t": 365,
     "ch": "HD",
     "clear": 389,
     "key": "sgx.hud.b12.1"
    }
   ],
   "flash": [
    {
     "t": 360,
     "level": "N4",
     "kind": "white",
     "color": 6,
     "dur": null
    },
    {
     "t": 361,
     "level": "N3",
     "kind": "white",
     "color": 3,
     "dur": null
    }
   ],
   "shake": [
    {
     "t": 360,
     "level": 10
    },
    {
     "t": 362,
     "level": 6
    },
    {
     "t": 366,
     "level": 3
    }
   ],
   "vfx": [
    {
     "t": 358,
     "fx": "jet_precharge"
    },
    {
     "t": 360,
     "fx": "jets_on"
    },
    {
     "t": 360,
     "fx": "ground_hit_glow"
    }
   ],
   "destruction": [
    {
     "t": 360,
     "op": "shaft"
    }
   ]
  },
  {
   "id": "B13",
   "act": "IV",
   "name": "O OLHO DO MUNDO",
   "ticks": [
    390,
    419
   ],
   "camera": [
    {
     "t": 390,
     "pos": {
      "around": "O",
      "r": 91.0,
      "az": -110,
      "el": 4
     },
     "look": "O",
     "ease": "linear",
     "fov": 70
    },
    {
     "t": 419,
     "pos": {
      "around": "O",
      "r": 150,
      "az": -100,
      "el": 20
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 60
    }
   ],
   "hud": [],
   "flash": [],
   "shake": [
    {
     "t": 390,
     "level": 1
    }
   ],
   "vfx": [
    {
     "t": 390,
     "fx": "ground_glow"
    },
    {
     "t": 400,
     "fx": "jets_fade"
    }
   ],
   "destruction": []
  },
  {
   "id": "B14",
   "act": "V",
   "name": "MARÉ",
   "ticks": [
    420,
    459
   ],
   "camera": [
    {
     "t": 420,
     "pos": {
      "around": "O",
      "r": 119.0,
      "az": -100,
      "el": -8
     },
     "look": "O",
     "ease": "step",
     "fov": 66,
     "cut": true
    },
    {
     "t": 459,
     "pos": {
      "around": "O",
      "r": 98.0,
      "az": -95,
      "el": -6
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 66
    }
   ],
   "hud": [
    {
     "t": 420,
     "ch": "SB",
     "clear": 459,
     "key": "sgx.hud.b14.0"
    },
    {
     "t": 430,
     "ch": "HD",
     "clear": 459,
     "key": "sgx.hud.b14.1"
    }
   ],
   "flash": [
    {
     "t": 446,
     "level": "N1",
     "kind": "white",
     "color": 2,
     "dur": null
    },
    {
     "t": 452,
     "level": "N1",
     "kind": "white",
     "color": 2,
     "dur": null
    },
    {
     "t": 457,
     "level": "N2",
     "kind": "white",
     "color": 7,
     "dur": null
    }
   ],
   "shake": [
    {
     "t": 420,
     "level": 3
    },
    {
     "t": 430,
     "level": 4
    },
    {
     "t": 438,
     "level": 5
    },
    {
     "t": 446,
     "level": 6
    },
    {
     "t": 452,
     "level": 7
    },
    {
     "t": 457,
     "level": 8
    }
   ],
   "vfx": [
    {
     "t": 420,
     "fx": "debris_rise"
    },
    {
     "t": 420,
     "fx": "ground_ripple_up"
    }
   ],
   "destruction": [
    {
     "t": 422,
     "op": "crater_slice"
    },
    {
     "t": 432,
     "op": "crater_slice"
    },
    {
     "t": 440,
     "op": "crater_slice"
    },
    {
     "t": 448,
     "op": "crater_slice"
    }
   ]
  },
  {
   "id": "B15",
   "act": "V",
   "name": "ESPAGUETE",
   "ticks": [
    460,
    499
   ],
   "camera": [
    {
     "t": 460,
     "pos": {
      "follow": "hero_chunk",
      "back": 3,
      "up": 1
     },
     "look": "hero_chunk",
     "ease": "step",
     "fov": 66,
     "cut": true
    },
    {
     "t": 499,
     "pos": {
      "follow": "hero_chunk",
      "back": 3,
      "up": 0.5
     },
     "look": "O",
     "ease": "inQuad",
     "fov": 90
    }
   ],
   "hud": [
    {
     "t": 470,
     "ch": "HD",
     "clear": 484,
     "key": "sgx.hud.b15.0"
    },
    {
     "t": 485,
     "ch": "HD",
     "clear": 494,
     "key": "sgx.hud.b15.1"
    },
    {
     "t": 495,
     "ch": "HD",
     "clear": 504,
     "key": "sgx.hud.b15.2"
    }
   ],
   "flash": [],
   "shake": [
    {
     "t": 460,
     "level": 4
    },
    {
     "t": 480,
     "level": 6
    },
    {
     "t": 495,
     "level": 7
    }
   ],
   "vfx": [
    {
     "t": 460,
     "fx": "hero_chunk"
    },
    {
     "t": 460,
     "fx": "speed_lines"
    },
    {
     "t": 470,
     "fx": "debris_streaks"
    }
   ],
   "destruction": []
  },
  {
   "id": "B16",
   "act": "V",
   "name": "A QUEDA",
   "ticks": [
    500,
    539
   ],
   "camera": [
    {
     "t": 500,
     "pos": {
      "follow": "hero_chunk",
      "back": 3,
      "up": 0.5
     },
     "look": "O",
     "ease": "linear",
     "fov": 90
    },
    {
     "t": 539,
     "pos": {
      "along": "O",
      "dist_to_shadow": 21.0
     },
     "look": "O",
     "ease": "inCubic",
     "fov": 120
    }
   ],
   "hud": [
    {
     "t": 505,
     "ch": "HD",
     "clear": 524,
     "key": "sgx.hud.b16.0"
    },
    {
     "t": 525,
     "ch": "HD",
     "clear": 539,
     "key": "sgx.hud.b16.1"
    }
   ],
   "flash": [
    {
     "t": 500,
     "level": "N3",
     "kind": "white",
     "color": 2,
     "dur": null
    }
   ],
   "shake": [
    {
     "t": 500,
     "level": 7
    },
    {
     "t": 515,
     "level": 5
    },
    {
     "t": 530,
     "level": 3
    }
   ],
   "vfx": [
    {
     "t": 500,
     "fx": "disk_plane_cross"
    },
    {
     "t": 505,
     "fx": "aberration_ring"
    },
    {
     "t": 510,
     "fx": "redshift_grade"
    },
    {
     "t": 520,
     "fx": "chunk_to_thread"
    }
   ],
   "destruction": []
  },
  {
   "id": "B17",
   "act": "VI",
   "name": "O ÚLTIMO OLHAR",
   "ticks": [
    540,
    579
   ],
   "camera": [
    {
     "t": 540,
     "pos": {
      "along": "O",
      "dist_to_shadow": 21.0
     },
     "look": "O",
     "ease": "linear",
     "fov": 120
    },
    {
     "t": 579,
     "pos": {
      "along": "O",
      "dist_to_shadow": 8.75
     },
     "look": "O",
     "ease": "outSine",
     "fov": 100,
     "stutter": [
      1,
      1,
      2,
      2,
      3,
      4,
      6,
      8
     ]
    }
   ],
   "hud": [
    {
     "t": 545,
     "ch": "HD",
     "clear": 559,
     "key": "sgx.hud.b17.0"
    },
    {
     "t": 560,
     "ch": "HD",
     "clear": 579,
     "key": "sgx.hud.b17.1"
    },
    {
     "t": 560,
     "ch": "HT",
     "value": 3
    }
   ],
   "flash": [],
   "shake": [
    {
     "t": 540,
     "level": 2
    },
    {
     "t": 560,
     "level": 1
    }
   ],
   "vfx": [
    {
     "t": 540,
     "fx": "redshift_grade"
    },
    {
     "t": 540,
     "fx": "aberration_ring_shrink"
    }
   ],
   "destruction": []
  },
  {
   "id": "B18",
   "act": "VI",
   "name": "CRUZAMENTO",
   "ticks": [
    580,
    599
   ],
   "camera": [
    {
     "t": 580,
     "pos": {
      "along": "O",
      "dist_to_shadow": 8.75
     },
     "look": "O",
     "ease": "linear",
     "fov": 100,
     "stutter": [
      8
     ]
    },
    {
     "t": 599,
     "pos": {
      "along": "O",
      "dist_to_shadow": 1.75
     },
     "look": "O",
     "ease": "inSine",
     "fov": 96
    }
   ],
   "hud": [],
   "flash": [],
   "shake": [],
   "vfx": [
    {
     "t": 580,
     "fx": "iris_close"
    },
    {
     "t": 590,
     "fx": "last_photon"
    }
   ],
   "destruction": []
  },
  {
   "id": "B19",
   "act": "VI",
   "name": "SILÊNCIO ABSOLUTO",
   "ticks": [
    600,
    619
   ],
   "camera": [
    {
     "t": 600,
     "pos": {
      "around": "O",
      "r": 150,
      "az": -100,
      "el": 35
     },
     "look": "O",
     "ease": "step",
     "fov": 55,
     "cut": true
    }
   ],
   "hud": [],
   "flash": [],
   "shake": [],
   "vfx": [
    {
     "t": 600,
     "fx": "screen_black"
    },
    {
     "t": 601,
     "fx": "despawn_debris"
    },
    {
     "t": 602,
     "fx": "spawn_remnant"
    },
    {
     "t": 604,
     "fx": "crater_rim_glow"
    }
   ],
   "destruction": [
    {
     "t": 600,
     "op": "crater_bulk"
    }
   ]
  },
  {
   "id": "B20",
   "act": "VII",
   "name": "DE FORA",
   "ticks": [
    620,
    659
   ],
   "camera": [
    {
     "t": 620,
     "pos": {
      "around": "O",
      "r": 150,
      "az": -100,
      "el": 35
     },
     "look": "O",
     "ease": "linear",
     "fov": 55
    },
    {
     "t": 659,
     "pos": {
      "around": "O",
      "r": 150,
      "az": -95,
      "el": 30
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 55
    }
   ],
   "hud": [],
   "flash": [],
   "shake": [],
   "vfx": [
    {
     "t": 620,
     "fx": "fade_in_from_black"
    },
    {
     "t": 620,
     "fx": "hawking_sparkles"
    }
   ],
   "destruction": []
  },
  {
   "id": "B21",
   "act": "VII",
   "name": "HAWKING",
   "ticks": [
    660,
    699
   ],
   "camera": [
    {
     "t": 660,
     "pos": {
      "around": "O",
      "r": 150,
      "az": -95,
      "el": 30
     },
     "look": "O",
     "ease": "linear",
     "fov": 55
    },
    {
     "t": 699,
     "pos": {
      "around": "O",
      "r": 105.0,
      "az": -90,
      "el": 18
     },
     "look": "O",
     "ease": "inOutSine",
     "fov": 50
    }
   ],
   "hud": [],
   "flash": [
    {
     "t": 660,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 672,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 682,
     "level": "N1",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 690,
     "level": "N2",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 696,
     "level": "N2",
     "kind": "white",
     "color": 1,
     "dur": null
    },
    {
     "t": 699,
     "level": "N2",
     "kind": "white",
     "color": 1,
     "dur": null
    }
   ],
   "shake": [],
   "vfx": [
    {
     "t": 660,
     "fx": "bh_shrink"
    },
    {
     "t": 660,
     "fx": "hawking_sparkles"
    },
    {
     "t": 660,
     "fx": "hawking_flicker"
    },
    {
     "t": 672,
     "fx": "hawking_flicker"
    },
    {
     "t": 682,
     "fx": "hawking_flicker"
    },
    {
     "t": 690,
     "fx": "hawking_flicker"
    },
    {
     "t": 696,
     "fx": "hawking_flicker"
    },
    {
     "t": 699,
     "fx": "hawking_flicker"
    }
   ],
   "destruction": []
  },
  {
   "id": "B22",
   "act": "VII",
   "name": "O ÚLTIMO CLARÃO",
   "ticks": [
    700,
    719
   ],
   "camera": [
    {
     "t": 700,
     "pos": {
      "around": "O",
      "r": 105.0,
      "az": -90,
      "el": 18
     },
     "look": "O",
     "ease": "linear",
     "fov": 50
    },
    {
     "t": 719,
     "pos": {
      "around": "O",
      "r": 140.0,
      "az": -90,
      "el": 22
     },
     "look": "O",
     "ease": "outSine",
     "fov": 52
    }
   ],
   "hud": [
    {
     "t": 704,
     "ch": "TT",
     "clear": 719,
     "key": "sgx.hud.b22.0"
    },
    {
     "t": 706,
     "ch": "TT2",
     "clear": 719,
     "key": "sgx.hud.b22.1"
    }
   ],
   "flash": [
    {
     "t": 700,
     "level": "N4",
     "kind": "white_soft",
     "color": 0,
     "dur": null
    }
   ],
   "shake": [],
   "vfx": [
    {
     "t": 700,
     "fx": "final_burst"
    },
    {
     "t": 704,
     "fx": "stars_twinkle"
    }
   ],
   "destruction": []
  }
 ],
 "letterbox": [
  {
   "t": 0,
   "vis": 0.5618
  },
  {
   "t": 47,
   "vis": 0.5618
  },
  {
   "t": 79,
   "vis": 0.41841,
   "ease": "inOutSine"
  },
  {
   "t": 240,
   "vis": 0.41841
  },
  {
   "t": 242,
   "vis": 0.37037,
   "ease": "outQuad"
  },
  {
   "t": 246,
   "vis": 0.41841,
   "ease": "outBack"
  },
  {
   "t": 459,
   "vis": 0.41841
  },
  {
   "t": 499,
   "vis": 0.35714,
   "ease": "inOutSine"
  },
  {
   "t": 539,
   "vis": 0.3125,
   "ease": "inOutSine"
  },
  {
   "t": 580,
   "vis": 0.3125
  },
  {
   "t": 590,
   "vis": 0.0,
   "ease": "inCubic"
  },
  {
   "t": 619,
   "vis": 0.0
  },
  {
   "t": 620,
   "vis": 0.0
  },
  {
   "t": 630,
   "vis": 0.5618,
   "ease": "outSine"
  },
  {
   "t": 719,
   "vis": 0.5618
  }
 ],
 "grade": [
  {
   "t": 0,
   "redshift": 0.0
  },
  {
   "t": 509,
   "redshift": 0.0
  },
  {
   "t": 539,
   "redshift": 0.5,
   "ease": "inQuad"
  },
  {
   "t": 579,
   "redshift": 0.95,
   "ease": "inOutSine"
  },
  {
   "t": 599,
   "redshift": 1.0
  },
  {
   "t": 600,
   "redshift": 0.0
  }
 ],
 "scaleCurve": [
  {
   "t": 240,
   "s": 1.0
  },
  {
   "t": 420,
   "s": 1.0
  },
  {
   "t": 539,
   "s": 1.35,
   "ease": "inQuad"
  },
  {
   "t": 620,
   "s": 0.6
  },
  {
   "t": 699,
   "s": 0.05,
   "ease": "inExpo"
  },
  {
   "t": 700,
   "s": 0.0
  }
 ],
 "halfOrbits": [
  74,
  87,
  99,
  112,
  124,
  135,
  146,
  156,
  166,
  176,
  185,
  194,
  202,
  209,
  216,
  222,
  227,
  232,
  236
 ],
 "disk": {
  "rings": [
   [
    8.4,
    14.0
   ],
   [
    14.0,
    20.3
   ],
   [
    20.3,
    27.3
   ],
   [
    27.3,
    34.65
   ],
   [
    34.65,
    42.0
   ]
  ],
  "ignite": {
   "ring5": 280,
   "ring4": 286,
   "ring3": 292,
   "ring2": 298,
   "ring1": 304
  },
  "omega": 90
 },
 "scene": {
  "k": 3.5,
  "oHeight": 49,
  "d0": 28.0,
  "shadowA": 4.24,
  "shadowB": 3.4,
  "shadowF": 7.28,
  "craterRadius": 45,
  "craterDepth": 42
 },
 "jets": {
  "tOn": 360,
  "tFade": [
   400,
   419
  ],
  "up": 180
 },
 "gwShell": {
  "t0": 240,
  "speed_blocks_per_tick": 21,
  "max_radius": 400,
  "camera_hit_tick_at_r140": 247
 },
 "sounds": [
  {
   "id": "sgx_void_in",
   "tick": 0,
   "end": 40,
   "volume": 0.9,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_point",
   "tick": 20,
   "end": 40,
   "volume": 1.0,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_twin",
   "tick": 40,
   "end": 60,
   "volume": 0.9,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_chirp",
   "tick": 60,
   "end": 240,
   "volume": 1.0,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_merge",
   "tick": 232,
   "end": 252,
   "volume": 1.0,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_ringdown",
   "tick": 241,
   "end": 280,
   "volume": 0.9,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_disk_ignite",
   "tick": 280,
   "end": 310,
   "volume": 0.9,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_disk_loop",
   "tick": 310,
   "end": 420,
   "volume": 0.75,
   "cutscene": true,
   "outside": false
  },
  {
   "id": "sgx_disk_loop_ext",
   "tick": 310,
   "end": 620,
   "volume": 0.75,
   "cutscene": false,
   "outside": true
  },
  {
   "id": "sgx_jet",
   "tick": 358,
   "end": 400,
   "volume": 1.0,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_pad",
   "tick": 400,
   "end": 460,
   "volume": 0.5,
   "cutscene": true,
   "outside": false
  },
  {
   "id": "sgx_tidal",
   "tick": 420,
   "end": 460,
   "volume": 1.0,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_fall",
   "tick": 460,
   "end": 540,
   "volume": 1.0,
   "cutscene": true,
   "outside": false
  },
  {
   "id": "sgx_horizon",
   "tick": 540,
   "end": 600,
   "volume": 0.9,
   "cutscene": true,
   "outside": false
  },
  {
   "id": "sgx_hawking",
   "tick": 620,
   "end": 700,
   "volume": 0.7,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_burst",
   "tick": 700,
   "end": 760,
   "volume": 1.0,
   "cutscene": true,
   "outside": true
  },
  {
   "id": "sgx_score_a",
   "tick": 0,
   "end": 600,
   "volume": 0.7,
   "cutscene": true,
   "outside": false
  },
  {
   "id": "sgx_score_b",
   "tick": 620,
   "end": 760,
   "volume": 0.7,
   "cutscene": true,
   "outside": false
  },
  {
   "id": "sgx_rhythm_a",
   "tick": 0,
   "end": 600,
   "volume": 1.0,
   "cutscene": true,
   "outside": false
  },
  {
   "id": "sgx_rhythm_b",
   "tick": 620,
   "end": 760,
   "volume": 1.0,
   "cutscene": true,
   "outside": false
  }
 ],
 "flashColors": [
  "#FFFFFF",
  "#F2F6FF",
  "#FFE2C4",
  "#C9C2FF",
  "#000000",
  "#DDE6FF",
  "#E9E4FF",
  "#FFD2A8"
 ]
};
export const HUD_TEXT = {
 "sgx.hud.b01.0": "ANOMALY DETECTED",
 "sgx.hud.b01.1": "GRAV. GRADIENT +0.003 g",
 "sgx.hud.b02.0": "SINGULARITY · A",
 "sgx.hud.b02.1": "MASS 36 M☉",
 "sgx.hud.b03.0": "SECOND BODY · 29 M☉",
 "sgx.hud.b03.1": "BINARY LOCKED",
 "sgx.hud.b04.0": "INSPIRAL · f 35 Hz · d 8.0",
 "sgx.hud.b05.0": "f 37 Hz · d 7.8",
 "sgx.hud.b05.1": "f 39 Hz · d 7.5",
 "sgx.hud.b05.2": "f 41 Hz · d 7.2",
 "sgx.hud.b06.0": "f 44 Hz · d 6.9",
 "sgx.hud.b06.1": "f 50 Hz · d 6.3",
 "sgx.hud.b07.0": "f 62 Hz · d 5.5",
 "sgx.hud.b07.1": "f 103 Hz · d 3.9",
 "sgx.hud.b07.2": "f 146 Hz · d 3.1",
 "sgx.hud.b07.3": "f 245 Hz",
 "sgx.hud.b08.0": "THEY BECAME ONE",
 "sgx.hud.b08.1": "MERGER · 62 M☉",
 "sgx.hud.b08.2": "ΔM = 3.0 M☉ → GRAVITATIONAL WAVES",
 "sgx.hud.b10.0": "ACCRETION",
 "sgx.hud.b10.1": "T 10⁷ K",
 "sgx.hud.b11.0": "SPIN a* = 0.67",
 "sgx.hud.b11.1": "ISCO 3 r_s",
 "sgx.hud.b12.0": "RELATIVISTIC JETS",
 "sgx.hud.b12.1": "v = 0.99 c",
 "sgx.hud.b14.0": "TIDAL FORCES",
 "sgx.hud.b14.1": "STRAIN 10⁹ g",
 "sgx.hud.b15.0": "r = 6 r_s",
 "sgx.hud.b15.1": "r = 3 r_s",
 "sgx.hud.b15.2": "r = 1.5 r_s · PHOTON SPHERE",
 "sgx.hud.b16.0": "r → r_s",
 "sgx.hud.b16.1": "z = 9.0",
 "sgx.hud.b17.0": "t → ∞",
 "sgx.hud.b17.1": "SIGNAL LOST",
 "sgx.hud.b22.0": "SINGULARITY",
 "sgx.hud.b22.1": "黑洞"
};
