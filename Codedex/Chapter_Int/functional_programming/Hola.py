def translator(language):
    translations = {
  'spanish': {'hello': 'hola', 'goodbye': 'adiós', 'thank you': 'gracias'},
  'french': {'hello': 'bonjour', 'goodbye': 'au revoir', 'thank you': 'merci'},
  'italian': {'hello': 'ciao', 'goodbye': 'arrivederci', 'thank you': 'grazie'}
}
    def translate_word(word):
        if word in translations[language]:
            return translations[language][word]
        else:
            return "Translation not found"

    return translate_word

translate_to_spanish = translator('spanish')
print(translate_to_spanish('hello')) # Output: hola
print(translate_to_spanish('goodbye'))
print(translate_to_spanish('thank you'))