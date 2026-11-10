"""
Mapeo oficial de las 16 regiones de Chile y sus principales comunas
para el banco de planimetría técnica y catastro territorial.
"""

REGIONES_CHILE = [
    {
        "region": "Arica y Parinacota",
        "zona_climatica": "Norte Árido / Desértico Costero (Zona 1)",
        "zona_sismica": "Zona 3 (Alta Sismicidad - NCh433)",
        "comunas": ["Arica", "Camarones", "Putre"]
    },
    {
        "region": "Tarapacá",
        "zona_climatica": "Desértico Costero (Zona 1)",
        "zona_sismica": "Zona 3 (Alta Sismicidad)",
        "comunas": ["Iquique", "Alto Hospicio", "Pozo Almonte", "Pica"]
    },
    {
        "region": "Antofagasta",
        "zona_climatica": "Desértico Costero y Marginal (Zona 1)",
        "zona_sismica": "Zona 3 (Alta Sismicidad)",
        "comunas": ["Antofagasta", "Calama", "Tocopilla", "Mejillones", "San Pedro de Atacama"]
    },
    {
        "region": "Atacama",
        "zona_climatica": "Desértico Transicional (Zona 2)",
        "zona_sismica": "Zona 3",
        "comunas": ["Copiapó", "Vallenar", "Caldera", "Chañaral"]
    },
    {
        "region": "Coquimbo",
        "zona_climatica": "Estepa Cálida / Semiárido (Zona 2)",
        "zona_sismica": "Zona 3",
        "comunas": ["La Serena", "Coquimbo", "Ovalle", "Illapel", "Vicuña"]
    },
    {
        "region": "Valparaíso",
        "zona_climatica": "Mediterráneo Costero (Zona 3)",
        "zona_sismica": "Zona 3",
        "comunas": ["Valparaíso", "Viña del Mar", "Quilpué", "Villa Alemana", "San Antonio", "Quillota", "Los Andes", "San Felipe"]
    },
    {
        "region": "Metropolitana de Santiago",
        "zona_climatica": "Mediterráneo Continental / Templado Cálido (Zona 3)",
        "zona_sismica": "Zona 2 (Intermedia - Depresión Central)",
        "comunas": ["Santiago Centro", "Providencia", "Las Condes", "Ñuñoa", "Maipú", "La Florida", "Puente Alto", "San Bernardo", "Quilicura", "Pudahuel", "Colina", "Melipilla", "Talagante"]
    },
    {
        "region": "Libertador General Bernardo O'Higgins",
        "zona_climatica": "Mediterráneo Templado (Zona 4)",
        "zona_sismica": "Zona 2 y 3",
        "comunas": ["Rancagua", "Machalí", "Rengo", "San Fernando", "Santa Cruz", "Pichilemu"]
    },
    {
        "region": "Maule",
        "zona_climatica": "Mediterráneo Templado Húmedo (Zona 4)",
        "zona_sismica": "Zona 2 y 3",
        "comunas": ["Talca", "Curicó", "Linares", "Constitución", "Cauquenes", "Molina"]
    },
    {
        "region": "Ñuble",
        "zona_climatica": "Templado de Transición (Zona 5)",
        "zona_sismica": "Zona 2 y 3",
        "comunas": ["Chillán", "Chillán Viejo", "San Carlos", "Quirihue", "Bulnes"]
    },
    {
        "region": "Biobío",
        "zona_climatica": "Templado Marítimo Lluvioso (Zona 5)",
        "zona_sismica": "Zona 3 (Alta Sismicidad de Borde Costero)",
        "comunas": ["Concepción", "Talcahuano", "San Pedro de la Paz", "Coronel", "Chiguayante", "Los Ángeles", "Tomé", "Lota"]
    },
    {
        "region": "La Araucanía",
        "zona_climatica": "Oceánico Lluvioso (Zona 5 / PDA Térmico)",
        "zona_sismica": "Zona 2 y 3",
        "comunas": ["Temuco", "Padre Las Casas", "Villarrica", "Pucón", "Angol", "Lautaro", "Victoria"]
    },
    {
        "region": "Los Ríos",
        "zona_climatica": "Oceánico Muy Lluvioso (Zona 6)",
        "zona_sismica": "Zona 3",
        "comunas": ["Valdivia", "La Unión", "Río Bueno", "Panguipulli", "Lago Ranco"]
    },
    {
        "region": "Los Lagos",
        "zona_climatica": "Marítimo Frío y Lluvioso (Zona 6 / 7)",
        "zona_sismica": "Zona 3",
        "comunas": ["Puerto Montt", "Puerto Varas", "Osorno", "Castro", "Ancud", "Quellón", "Frutillar"]
    },
    {
        "region": "Aysén del General Carlos Ibáñez del Campo",
        "zona_climatica": "Estepa Fría / Tundra de Lluvia (Zona 7 / PDA Extremo)",
        "zona_sismica": "Zona 2",
        "comunas": ["Coyhaique", "Puerto Aysén", "Chile Chico", "Cochrane"]
    },
    {
        "region": "Magallanes y de la Antártica Chilena",
        "zona_climatica": "Estepa Fría de Vientos Fuertes (Zona 7)",
        "zona_sismica": "Zona 2",
        "comunas": ["Punta Arenas", "Puerto Natales", "Porvenir", "Cabo de Hornos"]
    }
]
