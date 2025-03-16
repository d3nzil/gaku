# Cards
Cards are representations of knowledge in Gaku. The tests used for learning are generated from these Cards.

## Card options
When importing or editing these cards, there are options (depending on the card section) to select:
- `Enable Testing` - this select if the part will be in test - mostly used in vocabulary as option to skip rare or unimportant meanings for the word
- `Required` - when testing, at least one answer is always required for each field, this in addition will require this specific meaning or reading to be among the answers
- `Reading Type` - this allows you to select whether the reading is in hiragana, katakana or romaji
    - if the reading is mixed hiragana and katakana, select hiragana as it allows writing both - katakana is written by writing uppercase (using shift or caps lock when writing)

# Card types

## Vocabulary, Kanji, Radical and Onomatopoeia cards
Those are the basic Card types. Each of them holds knowledge about one word, kanji or radical.

## Multicards
Multicard is a special type of card, that is not created during import and instead needs to be created in the Multicard editor. It also requires some cards to already be in Gaku.

What this type of card does is, that it shows multiple questions of same type next to each other. The purpose being that if there is Kanji or word that you mistake for each other, to show them together, so you can see the differences and better remember them.

Clicking on the "Multi Card" in the top menu will show you the Multicard editor. If no Multicard is selected, you can either create a new one or search for existing one.

Before creating a new one, you need to select one of the supported types of Multicard: Vocab, Kanji or Radical. Once you select the Multicard type, click the `New Multi Card` button and the editor switches to edit mode then you will be able to search and add the selected type of card to the multicard as the search below switches from Multicard search to searching selected type of card.

Besides adding new cards to Multicard from search, you are also able to remove them, if they are no longer needed. If you wish, you can also add note (currently not displayed outside card listing) and hint (can be displayed in test).

Next is option to select what to test - reading and meaning for a card. Note this option has no effect for Radicals as for them both reading and meaning is always tested.
Finally, it is possible to add (but currently not remove) relevant sources for the Multicard.

Saving the card adds or updates it in database and discarding removes any changes to it.

Editing multicards is still work in progress and in future the Multicard editor should be moved to the Cards section.
