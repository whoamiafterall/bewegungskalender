from nicegui import ui

from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.nominatim import search_city


def location_filter():
	ui.input(label="Ort", placeholder="Stadt").on('update:model-value', handler=lambda e: update_location_card(e.args),
	                                              throttle=2.0).props('clearable').classes('w-full pl-3')
	
	location_card = ui.card().classes("ml-3 gap-0.5 border max-w-[260px] no-shadow")
	
	with location_card:
		location_card_city = ui.label("")
		location_distance_slider = ui.slider(min=1, max=10, step=0.25, value=1).on('update:model-value', lambda
			e: update_location_distance_slider_label(e.args), throttle=0.1).props('track-color=accent')
		location_distance_slider_label = ui.label("")
		
		
		def round_h_h(value):
			return round(value * 2) / 2
		
		
		def update_location_distance_slider_label(value):
			dis = round(value * value * 10)
			time_min = (0.5 + dis / 100)
			time_max = (0.5 + dis / 55)
			
			if time_max - time_min < 0.5:
				location_distance_slider_label.text = f"Radius: {dis}km ({round_h_h(time_max + (time_max - time_min) / 2)}h)"
			else:
				location_distance_slider_label.text = f"Radius: {dis}km ({round_h_h(time_min)}-{round_h_h(time_max)}h)"
		
		
		update_location_distance_slider_label(location_distance_slider.value)
		
		# TODO: finisch this up
		ui.checkbox(text="Mehrtägiges außerhalb Radius", value=True).disable()
		# TODO: finisch this up
		ui.checkbox(text="Online Events", value=True).disable()
	
	location_card.visible = False
	
	def update_location_card(value):
	# TODO: Fix TypeError: object of type 'NoneType' has no len()
		if len(value) <= 0:
			location_card.visible = False
		else:
			try:
				result = search_city(value)
				location_card.visible = True
				print(result[0])
				#location_card_coords = [float(result[0]["lat"]), float(result[0]["lon"])]
				location_card_city.text = result[0]["display_name"]
			
			except NoResultError:
				location_card.visible = False
	
	
	