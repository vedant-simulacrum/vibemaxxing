use std::fs;

use vibeproof_core::{Claim, decode_claim, encode_claim};

#[derive(serde::Deserialize)]
struct Corpus {
    valid: Vec<ValidVector>,
    invalid: Vec<InvalidVector>,
}

#[derive(serde::Deserialize)]
struct ValidVector {
    bytes_hex: String,
    accept: bool,
    claim: Claim,
}

#[derive(serde::Deserialize)]
struct InvalidVector {
    bytes_hex: String,
    accept: bool,
}

fn corpus() -> Corpus {
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../conformance/protocol/vibeproof-v1-vectors.json"
    );
    let text = fs::read_to_string(path).expect("shared vector corpus is checked in");
    serde_json::from_str(&text).expect("shared vector corpus is valid JSON")
}

fn decode_hex(value: &str) -> Vec<u8> {
    assert_eq!(value.len() % 2, 0, "hex is byte aligned");
    (0..value.len())
        .step_by(2)
        .map(|index| u8::from_str_radix(&value[index..index + 2], 16).expect("fixture hex"))
        .collect()
}

#[test]
fn claim_codec_encodes_and_decodes_shared_valid_vectors_byte_exactly() {
    // Given
    let corpus = corpus();

    for vector in corpus.valid {
        // When
        let expected = decode_hex(&vector.bytes_hex);
        let encoded = encode_claim(&vector.claim).expect("valid fixture encodes");
        let decoded = decode_claim(&expected).expect("valid fixture decodes");

        // Then
        assert_eq!(encoded, expected);
        assert_eq!(decoded, vector.claim);
        assert!(vector.accept);
    }
}

#[test]
fn claim_codec_rejects_every_shared_invalid_vector() {
    // Given
    let corpus = corpus();

    for vector in corpus.invalid {
        // When
        let result = decode_claim(&decode_hex(&vector.bytes_hex));

        // Then
        assert_eq!(result.is_ok(), vector.accept, "{}", vector.bytes_hex);
    }
}
