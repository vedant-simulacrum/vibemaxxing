use std::fs;

use vibeproof_core::{
    AccountingFixtureCorpus, PricingManifest, normalize, select_pricing_dataset,
    verify_pricing_dataset,
};

#[test]
fn accounting_fixtures_prove_deterministic_normalization() {
    // Given
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../conformance/accounting/accounting-v1-fixtures.json"
    );
    let fixtures: AccountingFixtureCorpus =
        serde_json::from_str(&fs::read_to_string(path).expect("fixtures"))
            .expect("typed accounting cases");
    assert_eq!(fixtures.version, "1");

    for fixture in fixtures.cases {
        // When
        let normalized = normalize(&fixture.observations).expect("fixture normalizes");

        // Then
        assert_eq!(normalized.billable, fixture.expected_billable);
        assert_eq!(normalized.status, fixture.status);
    }
}

#[test]
fn accounting_fixtures_reject_unknown_observation_fields() {
    // Given
    let fixture = r#"{"version":"1","cases":[{"id":"unknown-field","observations":[{"operation_id":"operation","provider_source_id":"provider-operation","observer_identity":"host","observer_source_id":"host-event","source":"authoritative","input":1,"output":2,"billable":3,"cache":0,"reasoning":0,"tool":0,"other":0,"category_relationships":{"cache":"included_in_input","reasoning":"included_in_output","tool":"informational_only","other":"exclusive"},"retry_reached_provider":true,"provider_failed":false,"historical_import":false,"duplicate_certainty":"certain","silently_ignored":true}],"expected_billable":3,"status":"counted"}]}"#;

    // When
    let result = serde_json::from_str::<AccountingFixtureCorpus>(fixture);

    // Then
    assert!(result.is_err());
}

#[test]
fn pricing_manifest_selects_historical_effective_dataset() {
    // Given
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../conformance/pricing/pricing-v1-manifest.json"
    );
    let manifest: PricingManifest =
        serde_json::from_str(&fs::read_to_string(path).expect("manifest")).expect("manifest JSON");

    // When
    let dataset = select_pricing_dataset(&manifest, "2026-01-02").expect("historical dataset");

    // Then
    assert_eq!(dataset.id, "pricing-v1");
    assert!(!manifest.signed);
    assert!(manifest.test_only);
    verify_pricing_dataset(
        &manifest,
        std::path::Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/../..")),
    )
    .expect("dataset digest");
}
