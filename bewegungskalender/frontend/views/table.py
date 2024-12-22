from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.formatting.format import event_time
from bewegungskalender.backend.io.config import MENU
from bewegungskalender.frontend.filter.filter import FilterController
from bewegungskalender.frontend.functions import loading, opacity
from bewegungskalender.frontend.navigation.router import ROUTER


# Create Table Page
@ROUTER.add(f"/{slugify(str(MENU['table']['label'].lower()))}")
def table_view():
    loading(MENU['table']['label'])

    columns = [
                {'name': 'start', 'label': 'Start', 'field': 'start', 'required': True, 'sortable': True, 'align': 'left'},
                {'name': 'title', 'label': 'Veranstaltung', 'field': 'title', 'sortable': True, 'align': 'left'},
                {'name': 'link', 'label': 'Link', 'field': 'link', 'align': 'left'},
                {'name': 'color', 'label': 'Color', 'field': 'color', 'align': 'left'},
            ]
    def use_filter():
        events = filterUI.events_using_filter()

        table = ui.table(title="Termine",
         columns=columns,
         rows=[{'start': event_time(event.start, event.end), 'title': event.summary, 'link': event.link, 'color': opacity(50, event.category.color)} for event in events],
        ).classes('bg-black text-white')
        table.add_slot('body-cell-title', '''
            <q-td :props="props">
                <a :href="props.row.link">{{ props.value }}</a>
            </q-td>''')
        table.add_slot('body-cell', r'''
            <q-td :props="props" color="props.row.color">
                {{ props.value }}
            </q-td>''')
        toggle(columns[2], False, table)
        #toggle(columns[3], False, table)

    def toggle(column: dict, visible: bool, table:ui.table) -> None:
        visible_columns = {column['name'] for column in columns}
        if visible:
            visible_columns.add(column['name'])
        else:
            visible_columns.remove(column['name'])
        table._props['columns'] = [column for column in columns if column['name'] in visible_columns]
        table.update()

    filterUI = Eventfilter(use_filter)
    use_filter()