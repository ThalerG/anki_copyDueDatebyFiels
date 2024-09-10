from anki.hooks import addHook
# import the main window object (mw) from aqt
from aqt import QAction, mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def testFunction() -> None:
    transfer_scheduling_data('Hanzi', 'Domino Text Input-43bf8', 'Recall', 'Domino Recognition and Stroke Order-6c462', 'Recall')

# create a new menu item, "test"
action = QAction("Copy cards", mw)
# set it to call testFunction when it's clicked 
qconnect(action.triggered, testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

import time

def transfer_scheduling_data(field_name: str, source_card_type_name: str, source_card_template_name: str, target_card_type_name: str, target_card_template_name: str):
    """
    Copies scheduling data from one card to another based on a matching field value,
    where the source card is of a specified template and the target card is of another specified template.

    :param mw.col: Anki collection object
    :param field_name: The name of the field to match between cards
    :param source_card_template_name: The name of the template for the source card
    :param target_card_template_name: The name of the template for the target card
    """
     
    # Find model IDs for both source and target templates
    source_model_id, target_model_id = None, None
    for model in mw.col.models.all():
        for tmpl in model['tmpls']:
            if (tmpl['name'] == source_card_template_name) and (model['name'] == source_card_type_name):
                source_model_id = model['id']
                source_ord = tmpl['ord']
            elif (tmpl['name'] == target_card_template_name) and (model['name'] == target_card_type_name):
                target_model_id = model['id']
                target_ord = tmpl['ord']

    if source_model_id is None or target_model_id is None:
        print("One or both specified templates could not be found.")
        return

    # Find all cards for the source model
    source_card_ids = mw.col.find_cards(f"\"note:{source_card_type_name}\" card:{source_ord+1}")
    target_card_ids = mw.col.find_cards(f"\"note:{target_card_type_name}\" card:{target_ord+1}")

    # Map field value to target card IDs
    field_to_target_card_ids = {}
    for card_id in target_card_ids:
        card = mw.col.get_card(card_id)
        note = card.note()
        field_value = note.fields[mw.col.models.field_map(note.note_type())[field_name][0]]
        if field_value not in field_to_target_card_ids:
            field_to_target_card_ids[field_value] = []
        field_to_target_card_ids[field_value] = card_id

    # Copy scheduling data from source to matching target cards
    for source_card_id in source_card_ids:
        source_card = mw.col.get_card(source_card_id)
        source_note = source_card.note()
        source_field_value = source_note.fields[mw.col.models.field_map(source_note.note_type())[field_name][0]]

        if source_field_value in field_to_target_card_ids:
            
            target_card_id = field_to_target_card_ids[source_field_value]
            target_card = mw.col.get_card(target_card_id)
            # Example of copying scheduling data, adjust as needed
            duedate_before = target_card.due
            target_card.due = source_card.due
            duedate_after = source_card.due

            target_card.ivl = source_card.ivl
            target_card.queue = source_card.queue
            target_card.factor = source_card.factor
            target_card.flags = source_card.flags
            target_card.lapses = source_card.lapses
            target_card.left = source_card.left
            target_card.mod = source_card.mod
            target_card.usn = -1
            target_card.odue = source_card.odue
            target_card.reps = source_card.reps

            # Use flush to save changes to the card
            mw.col.update_card(target_card)

            print(f"Replace scheduling data from card {source_card_id} (due {duedate_after}) to card {target_card_id} (due {duedate_before})")

            mw.col.db.execute("delete from notes where id = ?", source_card.nid)
            mw.col.db.execute("delete from cards where id = ?", source_card_id)

            mw.col.db.execute("update cards set id = ? where id = ?", source_card_id, target_card_id)
            mw.col.db.execute("update notes set usn = -1 where id = ?", target_card.nid)

    epoch = str(time.time()).replace(".", "")[0:13]
    mw.col.db.execute("update mw.col set mod = ?", epoch) 
    mw.col.save()

def print_card_types(mw.col):
    """
    Prints all cards from each card type (model) in the given Anki collection.

    :param mw.col: Anki collection object
    """
    for model in mw.col.models.all():
        for tmp in model['tmpls']:
            print(f"Model: {model['name']}, Card: {tmp['name']}")
        print('\n')

def print_template_name_of_each_card(mw.col):
    """
    Prints the template name of each card in the given Anki collection.

    :param mw.col: Anki collection object
    """
    for model in mw.col.models.all():
        model_id = model['id']
        templates = model['tmpls']
        card_ids = mw.col.find_cards(f"mid:{model_id}")
        for card_id in card_ids:
            card = mw.col.get_card(card_id)
            template_name = templates[card.ord]['name']
            print(f"Card ID: {card_id}, Template: {template_name}")


def get_card_due_date(mw.col, card_id: int) -> int:
    """
    Retrieves the due date of a card.

    :param mw.col: Anki collection object
    :param card_id: ID of the card
    :return: Due date of the card
    """
    card = mw.col.get_card(card_id)
    return card.due

if __name__ == '__main__':
    # Example usage
    # Replace 'path_to_your_collection.anki2' with the actual path to your Anki collection
    mw.col = Collection(r'C:\Users\Thaler\AppData\Roaming\Anki2\Usuário 1\collection.anki2')
    # print_card_types(mw.col)
    # print_template_name_of_each_card(mw.col)

    transfer_scheduling_data(mw.col, 'Hanzi', 'Domino Text Input-43bf8', 'Recall', 'Domino Recognition and Stroke Order-6c462', 'Recall')