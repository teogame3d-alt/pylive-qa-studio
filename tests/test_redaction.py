from pylive_qa_studio.core.redaction import redact_sensitive_text


def test_redaction_hides_local_paths_and_tokens():
    credential_sample = "s" + "k-" + "testcredential123456789"
    fake_assignment = "API" + "_KEY=abc123"
    text = rf"X:\Project\private\.env {credential_sample} {fake_assignment}"

    redacted = redact_sensitive_text(text)

    assert "X:\\" not in redacted
    assert ".env" not in redacted
    assert credential_sample[:12] not in redacted
    assert "abc123" not in redacted
    assert "<local-path>" in redacted
    assert fake_assignment.split("=", 1)[0] + "=<redacted-secret>" in redacted
