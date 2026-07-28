from app.infrastructure.preprocessing.text_preprocessor import TextPreprocessor


def test_removes_extra_spaces_and_invisible_characters() -> None:
    text = "Proje\u200b   adı\u00a0burada\ufeff."

    assert TextPreprocessor().clean(text) == "Proje adı burada."


def test_joins_word_split_at_line_end() -> None:
    text = "Bu bir dokü-\nman içeriğidir."

    assert TextPreprocessor().clean(text) == "Bu bir doküman içeriğidir."


def test_preserves_regular_hyphenated_words() -> None:
    text = "E-posta ve uçtan-uca iletişim korunmalı."

    assert TextPreprocessor().clean(text) == text


def test_preserves_paragraph_separation_without_excess_blank_lines() -> None:
    text = "Birinci paragraf.\n\n\n\nİkinci paragraf."

    assert TextPreprocessor().clean(text) == "Birinci paragraf.\n\nİkinci paragraf."


def test_does_not_merge_lines_without_hyphen() -> None:
    text = "Birinci satır\nikinci satır"

    assert TextPreprocessor().clean(text) == text
