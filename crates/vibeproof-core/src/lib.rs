use serde::{Deserialize, Serialize};
use thiserror::Error;

const MAX_CLAIM_BYTES: usize = 1024;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Claim {
    pub version: String,
    pub claim_id: [u8; 16],
    pub device_id: [u8; 16],
    pub key_id: [u8; 16],
    pub challenge: [u8; 32],
    pub issued_at: u64,
    pub sequence: u64,
    pub previous_claim_hash: [u8; 32],
    pub accounting_spec_version: u8,
    pub token_totals: TokenTotals,
    pub evidence_class: EvidenceClass,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TokenTotals {
    pub input: u64,
    pub output: u64,
    pub billable: u64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EvidenceClass {
    Authoritative,
    Structured,
    Observed,
    Estimated,
    Imported,
}

#[derive(Debug, Error, PartialEq, Eq)]
pub enum ProtocolError {
    #[error("invalid canonical CBOR")]
    InvalidCbor,
    #[error("invalid claim field")]
    InvalidField,
    #[error("claim exceeds the size limit")]
    Oversized,
}

pub fn encode_claim(claim: &Claim) -> Result<Vec<u8>, ProtocolError> {
    if claim.version != "v1" || claim.sequence == 0 {
        return Err(ProtocolError::InvalidField);
    }
    let mut output = Vec::with_capacity(180);
    output.push(0xab);
    encode_unsigned(&mut output, 1);
    encode_text(&mut output, &claim.version)?;
    encode_unsigned(&mut output, 2);
    encode_bytes(&mut output, &claim.claim_id)?;
    encode_unsigned(&mut output, 3);
    encode_bytes(&mut output, &claim.device_id)?;
    encode_unsigned(&mut output, 4);
    encode_bytes(&mut output, &claim.key_id)?;
    encode_unsigned(&mut output, 5);
    encode_bytes(&mut output, &claim.challenge)?;
    encode_unsigned(&mut output, 6);
    encode_unsigned(&mut output, claim.issued_at);
    encode_unsigned(&mut output, 7);
    encode_unsigned(&mut output, claim.sequence);
    encode_unsigned(&mut output, 8);
    encode_bytes(&mut output, &claim.previous_claim_hash)?;
    encode_unsigned(&mut output, 9);
    encode_unsigned(&mut output, u64::from(claim.accounting_spec_version));
    encode_unsigned(&mut output, 10);
    output.push(0xa3);
    encode_unsigned(&mut output, 1);
    encode_unsigned(&mut output, claim.token_totals.input);
    encode_unsigned(&mut output, 2);
    encode_unsigned(&mut output, claim.token_totals.output);
    encode_unsigned(&mut output, 3);
    encode_unsigned(&mut output, claim.token_totals.billable);
    encode_unsigned(&mut output, 11);
    output.push(evidence_to_u8(claim.evidence_class));
    if output.len() > MAX_CLAIM_BYTES {
        return Err(ProtocolError::Oversized);
    }
    Ok(output)
}

pub fn decode_claim(input: &[u8]) -> Result<Claim, ProtocolError> {
    if input.len() > MAX_CLAIM_BYTES {
        return Err(ProtocolError::Oversized);
    }
    let mut decoder = Decoder { input, offset: 0 };
    decoder.expect_map(11)?;
    let version = decoder.field(1, |value| value.text())?;
    let claim_id = decoder.field(2, |value| value.array_16())?;
    let device_id = decoder.field(3, |value| value.array_16())?;
    let key_id = decoder.field(4, |value| value.array_16())?;
    let challenge = decoder.field(5, |value| value.array_32())?;
    let issued_at = decoder.field(6, Decoder::unsigned)?;
    let sequence = decoder.field(7, Decoder::unsigned)?;
    let previous_claim_hash = decoder.field(8, |value| value.array_32())?;
    let accounting_spec_version = u8::try_from(decoder.field(9, Decoder::unsigned)?)
        .map_err(|_| ProtocolError::InvalidField)?;
    let token_totals = decoder.field(10, |value| {
        value.expect_map(3)?;
        Ok(TokenTotals {
            input: value.field(1, Decoder::unsigned)?,
            output: value.field(2, Decoder::unsigned)?,
            billable: value.field(3, Decoder::unsigned)?,
        })
    })?;
    let evidence_class = u8_to_evidence(
        u8::try_from(decoder.field(11, Decoder::unsigned)?)
            .map_err(|_| ProtocolError::InvalidField)?,
    )?;
    if decoder.offset != input.len() || version != "v1" || sequence == 0 {
        return Err(ProtocolError::InvalidField);
    }
    Ok(Claim {
        version,
        claim_id,
        device_id,
        key_id,
        challenge,
        issued_at,
        sequence,
        previous_claim_hash,
        accounting_spec_version,
        token_totals,
        evidence_class,
    })
}

fn encode_unsigned(output: &mut Vec<u8>, value: u64) {
    match value {
        0..=23 => output.push(value as u8),
        24..=255 => output.extend([0x18, value as u8]),
        256..=65_535 => output.extend([0x19, (value >> 8) as u8, value as u8]),
        65_536..=4_294_967_295 => output.extend([
            0x1a,
            (value >> 24) as u8,
            (value >> 16) as u8,
            (value >> 8) as u8,
            value as u8,
        ]),
        _ => output.extend([
            0x1b,
            (value >> 56) as u8,
            (value >> 48) as u8,
            (value >> 40) as u8,
            (value >> 32) as u8,
            (value >> 24) as u8,
            (value >> 16) as u8,
            (value >> 8) as u8,
            value as u8,
        ]),
    }
}

fn encode_bytes(output: &mut Vec<u8>, value: &[u8]) -> Result<(), ProtocolError> {
    encode_sized(output, 2, value.len())?;
    output.extend(value);
    Ok(())
}

fn encode_text(output: &mut Vec<u8>, value: &str) -> Result<(), ProtocolError> {
    encode_sized(output, 3, value.len())?;
    output.extend(value.as_bytes());
    Ok(())
}

fn encode_sized(output: &mut Vec<u8>, major: u8, length: usize) -> Result<(), ProtocolError> {
    let length = u64::try_from(length).map_err(|_| ProtocolError::Oversized)?;
    if length > 23 {
        output.push((major << 5) | 24);
        output.push(u8::try_from(length).map_err(|_| ProtocolError::Oversized)?);
    } else {
        output.push((major << 5) | u8::try_from(length).map_err(|_| ProtocolError::Oversized)?);
    }
    Ok(())
}

fn evidence_to_u8(value: EvidenceClass) -> u8 {
    match value {
        EvidenceClass::Authoritative => 0,
        EvidenceClass::Structured => 1,
        EvidenceClass::Observed => 2,
        EvidenceClass::Estimated => 3,
        EvidenceClass::Imported => 4,
    }
}

fn u8_to_evidence(value: u8) -> Result<EvidenceClass, ProtocolError> {
    match value {
        0 => Ok(EvidenceClass::Authoritative),
        1 => Ok(EvidenceClass::Structured),
        2 => Ok(EvidenceClass::Observed),
        3 => Ok(EvidenceClass::Estimated),
        4 => Ok(EvidenceClass::Imported),
        _ => Err(ProtocolError::InvalidField),
    }
}

struct Decoder<'a> {
    input: &'a [u8],
    offset: usize,
}

impl<'a> Decoder<'a> {
    fn take(&mut self) -> Result<u8, ProtocolError> {
        let value = *self
            .input
            .get(self.offset)
            .ok_or(ProtocolError::InvalidCbor)?;
        self.offset += 1;
        Ok(value)
    }
    fn unsigned(&mut self) -> Result<u64, ProtocolError> {
        self.head(0)
    }
    fn expect_map(&mut self, size: u64) -> Result<(), ProtocolError> {
        if self.head(5)? == size {
            Ok(())
        } else {
            Err(ProtocolError::InvalidField)
        }
    }
    fn field<T>(
        &mut self,
        key: u64,
        parse: impl FnOnce(&mut Self) -> Result<T, ProtocolError>,
    ) -> Result<T, ProtocolError> {
        if self.unsigned()? != key {
            return Err(ProtocolError::InvalidField);
        }
        parse(self)
    }
    fn text(&mut self) -> Result<String, ProtocolError> {
        let bytes = self.bytes_with_major(3)?;
        String::from_utf8(bytes.to_vec()).map_err(|_| ProtocolError::InvalidField)
    }
    fn array_16(&mut self) -> Result<[u8; 16], ProtocolError> {
        self.bytes_with_major(2)?
            .try_into()
            .map_err(|_| ProtocolError::InvalidField)
    }
    fn array_32(&mut self) -> Result<[u8; 32], ProtocolError> {
        self.bytes_with_major(2)?
            .try_into()
            .map_err(|_| ProtocolError::InvalidField)
    }
    fn bytes_with_major(&mut self, expected_major: u8) -> Result<&'a [u8], ProtocolError> {
        let length =
            usize::try_from(self.head(expected_major)?).map_err(|_| ProtocolError::InvalidCbor)?;
        let end = self
            .offset
            .checked_add(length)
            .ok_or(ProtocolError::InvalidCbor)?;
        let bytes = self
            .input
            .get(self.offset..end)
            .ok_or(ProtocolError::InvalidCbor)?;
        self.offset = end;
        Ok(bytes)
    }
    fn head(&mut self, expected_major: u8) -> Result<u64, ProtocolError> {
        let first = self.take()?;
        if first >> 5 != expected_major {
            return Err(ProtocolError::InvalidCbor);
        }
        let additional = first & 0x1f;
        let (value, minimum) = match additional {
            0..=23 => (u64::from(additional), 0),
            24 => (u64::from(self.take()?), 24),
            25 => (
                (u64::from(self.take()?) << 8) | u64::from(self.take()?),
                256,
            ),
            26 => (
                (u64::from(self.take()?) << 24)
                    | (u64::from(self.take()?) << 16)
                    | (u64::from(self.take()?) << 8)
                    | u64::from(self.take()?),
                65_536,
            ),
            27 => {
                let mut value = 0;
                for _ in 0..8 {
                    value = (value << 8) | u64::from(self.take()?);
                }
                (value, 4_294_967_296)
            }
            _ => return Err(ProtocolError::InvalidCbor),
        };
        if value < minimum {
            return Err(ProtocolError::InvalidCbor);
        }
        Ok(value)
    }
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AccountingFixtureCorpus {
    pub version: String,
    pub cases: Vec<AccountingFixture>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AccountingFixture {
    pub id: String,
    pub observations: Vec<Observation>,
    pub expected_billable: u64,
    pub status: AccountingStatus,
}
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Observation {
    pub operation_id: String,
    pub provider_source_id: String,
    pub observer_identity: String,
    pub observer_source_id: String,
    pub source: Source,
    pub input: u64,
    pub output: u64,
    pub billable: Option<u64>,
    pub cache: u64,
    pub reasoning: u64,
    pub tool: u64,
    pub other: u64,
    pub category_relationships: CategoryRelationships,
    pub retry_reached_provider: bool,
    pub provider_failed: bool,
    pub historical_import: bool,
    pub duplicate_certainty: DuplicateCertainty,
}
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CategoryRelationships {
    pub cache: CategoryRelationship,
    pub reasoning: CategoryRelationship,
    pub tool: CategoryRelationship,
    pub other: CategoryRelationship,
}
#[derive(Debug, Clone, Copy, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum CategoryRelationship {
    Exclusive,
    IncludedInInput,
    IncludedInOutput,
    IncludedInTotal,
    InformationalOnly,
}
#[derive(Debug, Clone, Copy, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum DuplicateCertainty {
    Certain,
    Uncertain,
}
#[derive(Debug, Clone, Copy, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "snake_case")]
pub enum Source {
    Imported,
    Estimate,
    Observed,
    Structured,
    Authoritative,
}
#[derive(Debug, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
#[serde(rename_all = "snake_case")]
pub enum AccountingStatus {
    Counted,
    Quarantined,
    Excluded,
}
#[derive(Debug, PartialEq, Eq)]
pub struct Normalized {
    pub billable: u64,
    pub status: AccountingStatus,
}

pub fn normalize(observations: &[Observation]) -> Result<Normalized, ProtocolError> {
    let active: Vec<&Observation> = observations
        .iter()
        .filter(|value| !value.historical_import && value.source != Source::Imported)
        .collect();
    if active.is_empty() {
        return Ok(Normalized {
            billable: 0,
            status: AccountingStatus::Excluded,
        });
    }
    if active
        .iter()
        .any(|value| value.duplicate_certainty == DuplicateCertainty::Uncertain)
    {
        return Ok(Normalized {
            billable: 0,
            status: AccountingStatus::Quarantined,
        });
    }
    let selected = active
        .into_iter()
        .max_by_key(|value| value.source)
        .ok_or(ProtocolError::InvalidField)?;
    if !selected.retry_reached_provider {
        return Ok(Normalized {
            billable: 0,
            status: AccountingStatus::Counted,
        });
    }
    let billable = if selected.provider_failed || selected.source == Source::Authoritative {
        selected.billable.unwrap_or(0)
    } else {
        selected.billable.unwrap_or_else(|| {
            selected
                .input
                .saturating_add(selected.output)
                .saturating_add(exclusive_category_total(selected))
        })
    };
    Ok(Normalized {
        billable,
        status: AccountingStatus::Counted,
    })
}

fn exclusive_category_total(observation: &Observation) -> u64 {
    [
        (observation.cache, observation.category_relationships.cache),
        (
            observation.reasoning,
            observation.category_relationships.reasoning,
        ),
        (observation.tool, observation.category_relationships.tool),
        (observation.other, observation.category_relationships.other),
    ]
    .into_iter()
    .filter_map(|(value, relationship)| {
        (relationship == CategoryRelationship::Exclusive).then_some(value)
    })
    .fold(0, u64::saturating_add)
}

#[derive(Debug, Deserialize)]
pub struct PricingManifest {
    pub version: String,
    pub signed: bool,
    pub test_only: bool,
    pub datasets: Vec<PricingDataset>,
}
#[derive(Debug, Deserialize)]
pub struct PricingDataset {
    pub id: String,
    pub path: String,
    pub sha256: String,
    pub effective_date: String,
    pub review_status: String,
}

pub fn select_pricing_dataset<'a>(
    manifest: &'a PricingManifest,
    date: &str,
) -> Result<&'a PricingDataset, ProtocolError> {
    if manifest.version != "1" || manifest.signed || !manifest.test_only {
        return Err(ProtocolError::InvalidField);
    }
    manifest
        .datasets
        .iter()
        .filter(|dataset| {
            dataset.effective_date.as_str() <= date
                && dataset.review_status == "test-only"
                && dataset.sha256.len() == 64
        })
        .max_by_key(|dataset| &dataset.effective_date)
        .ok_or(ProtocolError::InvalidField)
}

pub fn verify_pricing_dataset(
    manifest: &PricingManifest,
    root: &std::path::Path,
) -> Result<(), ProtocolError> {
    use sha2::{Digest, Sha256};

    for dataset in &manifest.datasets {
        let bytes =
            std::fs::read(root.join(&dataset.path)).map_err(|_| ProtocolError::InvalidField)?;
        let digest = format!("{:x}", Sha256::digest(bytes));
        if digest != dataset.sha256 {
            return Err(ProtocolError::InvalidField);
        }
    }
    Ok(())
}
