# About wordlists
Wordlist is a list of Japanese words you want to learn. It has to be one word per line, in dictionary form. 

# Preparing a wordlist
If not sure about the correct dictionary form, look up the word in [Jisho](https://jisho.org) or other dictionary and copy it from there. If the word is commonly in kana, but has kanji form, it is often better to put the kanji form in the list, to avoid having to avoid getting sometimes many words with same writing. But if there is only one or few words with the same kana, it can be used too. For book, manga and similar source it is best to write down the words in the order they appear. This is because when learning, the words appear in the order they are in the list. Note that the wordlist only contains vocabulary. The information about kanji and radicals are then added automatically.

Besides normal vocabulary, the Gaku also supports Onomatopoeia (sound effects and such, usually found in manga). Since these are stored in separate dictionary, they need to be prefixed with `@` symbol currently. These also need to be written in hiragana or katakana, so the dictionary lookup finds them. For example:
```
@あっはっはっはっ
```

Additionally, you can add comments and hints for the words like:
```
# lines like this starting with # are considered a comments
言葉 - anything after a - is considered a note for the word
```

Comments are there only for better organization - you can use them for example to note a page where the word appeared.

Hints are imported together with the word and can be displayed in Gaku when studying.

Once you have the list written down, you can save the file in case you need it again later, or want to share it with others. For sharing the file should be saved as text with .txt extension and in UTF-8 encoding.

For example of such wordlist, there are a few of them included in the vocab-text directory (folder).

Later, I plan to add export for the cards, so sharing should become much easier.

# Sharing wordlists
If you want to help and share your wordlist with the future version of Gaku, just note that it needs one of the two following licenses selected:
- https://creativecommons.org/licenses/by-sa/4.0/
- https://creativecommons.org/licenses/by-nc-sa/4.0/

Licensing is needed to ensure people can use the wordlist and I picked those two to keep it simple, by limiting the options (I might be persuaded to accept CC0). You can of course share the lists elsewhere under any license you want.
