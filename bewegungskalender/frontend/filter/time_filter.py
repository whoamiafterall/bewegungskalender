from nicegui import ui

def timespan_filter():
	timespan_slider_label = ui.label("").classes('pl-3 font-medium')
	timespan_slider = (ui.slider(min=10, max=180, step=10, value=30)
                .on('update:model-value', lambda e: update_timespan_slider_label(e.args), throttle=0.1)
	            .props('thumb-color=accent selection-color=accent')
	            .classes('pl-3'))
	
	def update_timespan_slider_label(value):
		timespan_slider_label.text = f"Events der nächsten {value} Tage"
	
	update_timespan_slider_label(timespan_slider.value)
	
def duration_filter():
	(ui.select(["Mehrtägig", "1 Tag", "Stunden"], label="Dauer", value=["Mehrtägig", "1 Tag", "Stunden"],
	           multiple=True, clearable=True).classes("pl-3 w-full my-1")).props("filled color=secondary")