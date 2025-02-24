# Gaku

# Long term goal
To have a tool for learning Japanese vocabulary, kanji and radicals, where the flashcards would be ordered based on some manga, book, article, etc.
So pretty much tool to learn vocabulary for the book, manga...

# Current status

# How to use

## Starting Gaku
See the instructions in the [Readme](../../README.md)

## Quicstart
- create source for the vocabulary
- write a list of vocabulary, one word per line, dictionary form (jisho.org is your friend)
- paste the vocabulary into the text field on import, click `Generate Imports`, wait a bit
- review the generated cards
- once you are happy, select the source and click the `Import cards` button
- go to the Select test page and start studying
- practice daily - the hard part (:


## Creating a source
Source is used to tell where the word comes from - book, manga, textbook, etc. While not strictly needed, I do recommend using it, to keep things organized.

To create a new source, go to the Sources section. In the `Add source` section there will be two text inputs - `Source Name` and `Source Section`. The name is intended for the name of the book or other source - e.g "Ranma 1/2", the section for specific book and chapter - e.g. "Book 1, Chapter 2". Only the name is required.

Once you fill in the fields, click the `Add Source` button and it should be added. If not, see the reporting problems section.

Admiteddly, this organization is not ideal, but was good enough to get started. Hopefully when the more important parts will be finished, this will get improved too.

## Preparing a wordlist
Wordlist is a list of Japanese words you want to learn. It has to be one word per line, in dictionary form. If not sure about the correct dictionary form, look up the word in https://jisho.org or other dictionary and copy it from there. If the word is commonly in kana, but has kanji form, it is often better to put the kanji form in the list, to avoid having to avoid getting sometimes many words with same writing. But if there is only one or few words with the same kana, it can be used too. For book, manga and similar source it is best to write down the words in the order they appear. This is because when learning, the words appear in the order they are in the list. Note that the wordlist only contains vocabulary. The information about kanji and radicals are then added automatically.

Additionally, you can add comments and hints for the words like:
```
# lines like this starting with # are considered a comments
言葉 - anything after a - is considered a note for the word
```

Comments are there only for better organization - you can use them for example to note a page where the word appeared.

Hints are imported together with the word and can be displayed in Gaku when studying.

Once you have te list written down, you can save the file in case you need it again later, or want to share it with others. For sharing the file should be saved as text with .txt extension and in UTF-8 encoding.

For example of such wordlist, there are a few of them included in the vocab-text directory (folder).

Later, I plan to add export for the cards, so sharing should become much easier.

If you want to help and share your wordlist with the future version of Gaku, just note that it needs one of the two following licenses selected:
- https://creativecommons.org/licenses/by-sa/4.0/
- https://creativecommons.org/licenses/by-nc-sa/4.0/

Licensing is needed to ensure people can use the wordlist and I picked those two to keep it simple, by limiting the options (I might be persuaded to accept CC0). You can of course share the lists elsewhere under any license you want.

## Importing a wordlist
Before importing new vocabulary, it is best to have a Source created, as described above.

To import a wordlist, go to import section. In there you have two options - if you have a wordlist created as described in previous section, you can just load file using the browse button. After that the contents of the file should appear in the box below.

Alternatively you can copy the wordlist and paste it in the box below the browse button.

Once the list of words is there, click the `Generate imports` button. It might take a bit, but after a moment a list of generated cards should appear next to it in the `Generated imports` section. If there were any problems during the card generation, messages will appear below the Generate imports button.

Note: Card in Gaku are a piece of knowledge (vocabulary, kanji...) to study. At the moment these types of cards - radicals, kanji, vocabulary and multicards. (There are custom questions, but these are currently not ready for use.)

Check the generated cards - in Japanese the same kanji or kana can be used for multiple words, so sometimes there are multiple different cards. In case there is a card that is not relevant, you can remove it using the delete button on top of the card.

In addition to extra cards, the dictionary sometimes contains entries like `to be able to ..., can ...` as single entry and it is not easy to handle special cases like this, so these need to be checked manually.

For vocabulary cards you can also disable testing of some meanings, as some words can have a lot of meanings and some of them might not be relevant.

There is also option mark some readings, writings, meanings as required. Required means that it will be required in test as answers. Not required means the answer is optional - not needed, but accepted.

Once you are happy with the list, select a source (or multiple if needed for some reason) and click the `Import cards` button on the left. After a moment, the carts will be imported and the Generated imports section will be cleared. Now the cards are ready to be studied.

Note that while I have some plans on how to avoid the need to check the cards, it will take some time to get it working.

## Multicards
Multicard is a special type of card, that is not created during import and instead needs to be created in the Multicard editor.It also requires some cards to already be in Gaku.

What this type of card does is, that it shows multiple questions of same type next to each other. The purpose being that if there is Kanji or word that you mistake for each other, to show them together, so you can see the differences and better remember them.

Clicking on the "Multi Card" in the top menu will show you the Multicard editor. If no Multicard is selected, you can either create a new one or search for existing one.

Before creating a new one, you need to select one of the supported types of Multicard: Vocab, Kanji or Radical. Once you select the Multicard type, click the `New Multi Card` button and the editor switches to edit mode then you will be able to search and add the selected type of card to the multicard as the search below switches from Multicard search to searching selected type of card.

Besides adding new cards to Multicard from search, you are also able to remove them, if they are no longer needed. If you wish, you can also add note (currently not displayed outside card listing) and hint (can be displayed in test).

Next is option to select what to test - reading and meaning for a card. Note this option has no effect for Radicals as for them both reading and meaning is always tested.
Finally, it is possible to add (but currently not remove) relevant sources for the Multicard.

Saving the card adds or updates it in database and discarding removes any changes to it.

Editing multicards is still work in progress and in future the Multicard editor should be moved to the Cards section.


## Learning, testing and practice
### Selecting what to learn, test or practice
To learn or practice click the `Select Test` in the top menu.

There are multiple things that can show there.

1. Test status section - this will show you how many due cards and new cards are there. New cards are the ones you haven't learned yet in Gaku. Due cards are the ones scheduled to be tested again based on their test history. To decide when that happens Gaku uses spaced repetition (SRS) - a technique based on how human memory works to decide best time to remind the cards.

2. Next to the test status section there is forecast of upcoming due cards. This is there so you know what to expect in coming days. Initially there will be only zeros, but once you start learning, it will fill up.

3. Not visible initially, but when you have started test and not finished it yet, below the Test section there will be small section showing current test status and a button to jump back to the session

4. New Test Settings - here you can customize what and how will you learn and practice.
    - Test type 
        - Standard test (default) - this mode will update the spaced repetition scheduling based on correct and incorrect answers. This mode is recommended in most cases.
        - Practice test (not marked) - this mode will not affect the card scheduling. It is best used for when you need to practice for class or test and don't want to mess up your schedule.
    - Number of cards to study - this one might sound self explanatory, but you might be surprised to see higher number displayed next to question count in the test. This is because for e.g. vocabulary card, there is question about meaning and another about reading, resulting in 2 questions for the card.
    - Generate extra questions - checking this (default) will add extra questions to the test.
        - For vocabulary cards, there will be extra question about kanji the vocabulary contains.
        - For kanji cards there will be extra question about which radical is associated with it.
        - There are no extra questions for other types of cards.
    - Select source - by default, when learning new vocabulary, Gaku presents you the oldest vocabulary first, in order you originally imported it. If you want to study something specific (e.g for book you want to read), you can select source (or multiple sources) to study. When source or sources are selected, Gaku will present you the cards belonging to that source instead of the default order.
    - Select card types - this is mostly useful for practice mode and Multicards - here you can select one or more of types of card and then Gaku will present you with only questions for selected card types. By default (empty selection), it will present you with all card types. The reason for suggesting practice mode is that new cards are learned in order and hiding some card types would make learning harder. For due card it is best to study them all regularly. But when you need e.g. to practice vocabulary for test, this is when this option comes handy. This also comes handy when you have have Multicards with sets of Kanji (or words) that you mistake for each other and only want to practice these.

5. Next are buttons for starting practice and test:
    - Study Due Cards - this is for reminding learned cards, based on the SRS scheduling
    - Study New Cards - this is for learning new vocabulary and will present you questions in order. Specifically, it will first show you radical question (if not learned yet) for a kanji, then that kanji (again, if not learned yet) and then finally a new vocabulary consisting of the kanji.
    - Study Any State Cards - this will present you with all cards that match current test settings. So if you want to study cards (e.g. for test), when they are not yet due, use this.

6. Recent mistakes is the final section. It shows how many cards that had at least one of questions answered incorrectly in the last week. Note that only the most recent mistake is counted. Clicking the `[Number] day ago` text will set the time clicked in the right section. In the right section, if you want to practice the cards with mistakes, you can set how far in past to select cards with mistakes. Below that you will see how many cards will be practiced as the amount depends on the test settings. And finally there is button to practice the cards.

With that, the test selection is covered.

## Learning and practicing
Once you start the test, Gaku will switch to test screen. On top there will be status of the current test, displaying how many cards, and questions were answered correctly. There is also option to display or hide question hints by clicking the `Hint off` or `Hint on` next to the status.

Under the status will be one of the questions and one or more text inputs. Above each of them, there is text telling you what kind of answer is expected in it. On the right side of the input, there is hiragana, katakana or romaji symbol. This symbol will tell you what your input will be converted into. Most of the time, it will be matching the answer type on the card, but in some cases it might be incorrect. If that is the case, you can click the symbol and it will switch the mode in cycle.

When writing down answer, multiple answers can be written in one field (e.g. when kanji has multiple On readings). All you need to do is to separate each answer by writing coma. Both English and Japanese comas are accepted. Once you write your answer in the field, pressing Enter key will move to the next answer input, or if it was the last one, it will check if the answer is correct.

In case you made typo, or mistake, you can just edit the answer and either click the Re-check button or keep pressing Enter key until it is checked by leaving the last answer input. There is also button to force marking the answer as correct and button to get next question. The next question can be also loaded by pressing Enter key again after the answer is checked. Also, after mistake the correct answers for the question are displayed, with **bold** meaning this answer is required. The answers in normal font are optional, but always at least one of them is needed.

Another thing to note after incorrect answer is that the same question will be displayed again and this will repeat until you answer correctly. This is done to ensure you know how to answer the card. In future it will be possible to disable this behavior. Also after any mistake, 2 correct answers for this specific question are then needed (not counting the one right after mistake). I did it this way, because I noticed that when learning elsewhere, I keep repeating the same mistake and then correcting it. Requiring 2 answers in a row hopefully will help remember me the correct answer by seeing the correct more often than the wrong one.

AFter correct answer, there will be button to mark the answer as incorrect (e.g in case you mistaken one kanji for another with same reading).

Then there is `Show Card Info` button, that will display the currently tested card, so you can check or review it.

Finally there are few keyboard shortcuts:
- `F2` will toggle hint on and off
- `F3` will show and hide the correct answer (only after current answer is checked)
- `F4` will show and hid the card for this question

### Few notes about testing and writing answers
The spaced repetition is only updated during testing when:
- answer is answered incorrectly
- all answers are answered correctly, without mistake

In both cases the update happens only when next card is loaded or test finishes. So when you see check result, it was not updated yet. This is to allow easy way to change incorrect answer to correct one (or the other way).

The conversion of text to hiragana and katakana uses library called Wanakana. This is used in Jisho dictionary, Wanikani and probably others. If you used one of these, writing is pretty much same as there. Just in case - to write small "tsu" character type "ltsu" (mostly useful for kanji readings). There are more combinations like this, but these will be documented later as it was not priority for first version.

Switching input conversion using the alphabet button next to an input might result in unwanted conversion of existing input to katakana or hiragana (romaji is unaffected). I don't know how to fix this problem yet, it is a bit tricky. If you need to mix hiragana and katakana, use hiragana mode and write in UPPERCASE to get katakana.

The order of questions outside learning new cards is random. It is pretty common to be halfway done answering questions and only have one or two cards completed. If this is something you don't want, best solution for now is to use small amount (5-10) of cards for each session.
