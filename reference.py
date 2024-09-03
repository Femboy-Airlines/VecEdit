light_stylesheet = """
	QWidget {
		background-color: white;
		color: black;
	}
	QPushButton {
		background-color: lightgray;
		color: black;
	}
	QTabWidget::pane {
		border: 1px solid lightgray;
	}
	QTabBar::tab {
		background: lightgray;
		color: black;
		padding: 5px;
	}
	QTabBar::tab:selected {
		background: white;
		border: 1px solid lightgray;
		border-bottom-color: white;
	}
	QTreeView {
		background-color: white;
		color: black;
	}
	QTreeView::item:selected {
		background-color: lightgray;
		color: black;
	}
"""

dark_stylesheet = """
	QWidget {
		background-color: #2d2d2d;
		color: white;
	}
	QPushButton {
		background-color: #3d3d3d;
		color: white;
	}
	QTabWidget::pane {
		border: 1px solid #3d3d3d;
	}
	QTabBar::tab {
		background: #3d3d3d;
		color: white;
		padding: 5px;
	}
	QTabBar::tab:selected {
		background: #2d2d2d;
		border: 1px solid #3d3d3d;
		border-bottom-color: #2d2d2d;
	}
	QTreeView {
		background-color: #2d2d2d;
		color: white;
	}
	QTreeView::item:selected {
		background-color: #3d3d3d;
		color: white;
	}
	QHeaderView::section {
		background-color: #3d3d3d;
		color: white;
		padding: 4px;
		border: 1px solid #3d3d3d;
	}
"""

unit_list = [
    "vec_sawblade",
    "vec_triangle",
    "vec_fighter",
    "vec_bomber",
    "vec_carrier",
    "vec_hammerhead"
]

resource_list = [
	"resource_gold",
	"resource_crystallite",
	"resource_essence",
	"resource_iridium",
	"resource_lumina",
	"resource_nitrium",
	"resource_osmium",
	"resource_celite",
	"resource_voidstone",
	"resource_phantomite",
	"resource_abyssminite",
	"resource_alcheminium",
	"resource_gilded_crystal",
	"resource_ether_shard",
	"resource_liquid_essence",
	"resource_arcana_steel",
	"resource_liquid_lumina",
	"resource_kinetic_cellite",
	"resource_liquid_nitrium",
	"resource_dark_gold",
	"resource_reanimated_shard",
	"resource_glimmering_gem",
	"resource_arcanium_battery",
	"resource_reactive_cellite",
	"resource_phantom_core",
	"resource_shaded_gem",
	"resource_abyss_core",
]

building_list = [
	"vec_storage",
	"vec_wall",
	"vec_reclaimer",
	"vec_builder_port",
	"vec_barrier",
	"vec_cargo_drone",
	"vec_cargo_port",
	"vec_shotgunner",
	"vec_foundry",
	"vec_node_reactor",
	"vec_builder_drone",
	"vec_sweeper",
	"vec_ranger",
	"vec_collector",
	"vec_depot",
	"vec_liquidator",
	"vec_manufacturer",
	"vec_laborator",
	"vec_buffer",
	"vec_repeater",
	"vec_basic_core",
	"vec_hive_core",
	"vec_hive_cell",
	"vec_core_assembler",
	"vec_artillery",
	"vec_ammo_forge",
	"vec_bullet_shield",
	"vec_pulsar",
	"vec_generator"
]

all_techs = [
    "tech_main",
    "tech_cargo_port",
    "tech_collector",
    "tech_gilded_crystal",
    "tech_gold",
    "tech_laboratory",
    "tech_liquid_essence",
    "tech_storage",
    "tech_foundry",
    "tech_liquidator",
    "tech_sweeper",
    "tech_redeemer",
    "tech_manufacturer",
    "tech_ammo_forge",
    "tech_core_assembler",
    "tech_artillery",
    "tech_striker",
    "tech_depot",
    "tech_phantom_core",
    "tech_arcana_steel",
    "tech_pulsar",
    "tech_essence",
    "tech_repeater",
    "tech_builder_port",
    "tech_crystallite",
    "tech_node_reactor",
    "tech_ranger",
    "tech_reclaimer",
    "tech_shotgunner",
    "tech_wall",
    "tech_glimmering_gem",
    "tech_plasma_round",
    "tech_artillery_shell",
    "tech_ether_shard",
    "tech_buffer",
    "tech_filter",
    "tech_lumina",
    "tech_arcanium_battery",
    "tech_barrier",
    "tech_liquid_lumina",
    "tech_iridium",
    "tech_reactive_cellite",
    "tech_kinetic_cellite",
    "tech_nitrium",
    "tech_driller",
    "tech_celite",
    "tech_generator",
    "tech_beacon",
    "tech_bullet_shield",
    "tech_decorations",
    "tech_courier_port",
    "tech_fabricator_port",
    "tech_enforced_tile",
    "tech_caution_tile",
    "tech_circular_tile",
    "tech_basic_missile",
    "tech_plains_gateway",
    "tech_phantom_tech",
    "tech_abyss_gateway",
    "tech_frigid_gateway",
    "tech_liquid_nitrium",
    "tech_arcana_battery",
    "tech_illuminator",
    "tech_spotter",
    "tech_phantomite_fragment",
    "tech_alcheminium",
    "tech_voidstone",
    "tech_osmium",
    "tech_reanimated_shard",
    "tech_tesla",
    "tech_phantom_lab",
    "tech_alchemized_iridium",
    "tech_gargoyle",
    "tech_alchemator",
    "tech_abyss_fragment",
    "tech_abyss_fragment",
    "tech_dark_gold",
    "tech_dark_builder_port",
    "tech_atomizer",
    "tech_energy_wall",
    "tech_alchemized_nitrium",
    "tech_shaded_gem",
    "tech_abyss_core",
    "tech_alchemized_crystallite",
    "tech_radar",
    "tech_orbitar",
    "tech_scyther"
]