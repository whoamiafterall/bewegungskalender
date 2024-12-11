from nicegui import ui

def timespan_filter():
	timespan_slider_label = ui.label("").classes('font-medium')
	timespan_slider = ui.slider(min=10, max=180, step=10, value=30).on('update:model-value',
	                                                                        lambda e: update_timespan_slider_label(
		                                                                        e.args), throttle=0.1).props('track-color=accent')
	
	def update_timespan_slider_label(value):
		timespan_slider_label.text = f"Events der nächsten {value} Tage"
	
	
	update_timespan_slider_label(timespan_slider.value)