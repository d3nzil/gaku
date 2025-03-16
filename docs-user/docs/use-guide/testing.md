# Learning and practicing
Once you start the test, Gaku will switch to test screen. On top there will be status of the current test, displaying how many cards, and questions were answered correctly. There is also option to display or hide question hints by clicking the `Hint off` or `Hint on` next to the status.

Under the status will be one of the questions and one or more text inputs. Above each of them, there is text telling you what kind of answer is expected in it. On the right side of the input, there is hiragana, katakana or romaji symbol. This symbol will tell you what your input will be converted into. Most of the time, it will be matching the answer type on the card, but in some cases it might be incorrect. If that is the case, you can click the symbol, and it will switch the mode in cycle.

When writing down answer, multiple answers can be written in one field (e.g. when kanji has multiple On readings). All you need to do is to separate each answer by writing coma. Both English and Japanese comas are accepted. Once you write your answer in the field, pressing Enter key will move to the next answer input, or if it was the last one, it will check if the answer is correct.

In case you made typo, or mistake, you can just edit the answer and either click the Re-check button or keep pressing Enter key until it is checked by leaving the last answer input. There is also button to force marking the answer as correct and button to get next question. The next question can be also loaded by pressing Enter key again after the answer is checked. Also, after mistake the correct answers for the question are displayed, with **bold** meaning this answer is required. The answers in normal font are optional, but always at least one of them is needed.

Another thing to note after incorrect answer is that the same question will be displayed again and this will repeat until you answer correctly. This is done to ensure you know how to answer the card. In the future it will be possible to disable this behavior. Also after any mistake, 2 correct answers for this specific question are then needed (not counting the one right after mistake). I did it this way, because I noticed that when learning elsewhere, I keep repeating the same mistake and then correcting it. Requiring 2 answers in a row hopefully will help remember me the correct answer by seeing the correct more often than the wrong one.

After correct answer, there will be button to mark the answer as incorrect (e.g. in case you have mistaken one kanji for another with same reading).

Then there is `Show Card Info` button, that will display the currently tested card, so you can check or review it.

Finally, there are few keyboard shortcuts:
- `F2` will toggle hint on and off
- `F3` will show and hide the correct answer (only after current answer is checked)
- `F4` will show and hid the card for this question

# Few notes about testing and writing answers
The spaced repetition is only updated during testing when:
- answer is answered incorrectly
- all answers are answered correctly, without mistake

In both cases the update happens only when next card is loaded or test finishes. So when you see check result, it was not updated yet. This is to allow easy way to change incorrect answer to correct one (or the other way).

The conversion of text to hiragana and katakana uses library called Wanakana. This is used in Jisho dictionary, Wanikani and probably others. If you used one of these, writing is pretty much same as there. Just in case - to write small "tsu" character type "ltsu" (mostly useful for kanji readings). There are more combinations like this, but these will be documented later as it was not priority for first version.

Switching input conversion using the alphabet button next to an input might result in unwanted conversion of existing input to katakana or hiragana (romaji is unaffected). I don't know how to fix this problem yet, it is a bit tricky. If you need to mix hiragana and katakana, use hiragana mode and write in UPPERCASE to get katakana.

The order of questions outside learning new cards is random. It is pretty common to be halfway done answering questions and only have one or two cards completed. If this is something you don't want, the best solution for now is to use small amount (5-10) of cards for each session.
