"use strict";

const escapeText = (value) => String(value ?? "");

async function loadEvidence() {
  const status = document.getElementById("release-status");
  const list = document.getElementById("evidence-list");
  try {
    const response = await fetch("data/current/evidence.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const documentData = await response.json();
    const records = Array.isArray(documentData.records) ? documentData.records : [];
    status.textContent = `${records.length} record${records.length === 1 ? "" : "s"} · generated ${escapeText(documentData.generated_at)}`;
    for (const record of records) {
      const article = document.createElement("article");
      article.className = "record";
      const meta = document.createElement("p");
      meta.className = "record-meta";
      meta.textContent = `${escapeText(record.record_id)} · ${escapeText(record.evidence_type)} · ${escapeText(record.published_date)}`;
      const title = document.createElement("h3");
      title.textContent = escapeText(record.title);
      const summary = document.createElement("p");
      summary.textContent = escapeText(record.summary);
      const limitation = document.createElement("p");
      limitation.className = "limitation";
      limitation.textContent = `Limitation: ${escapeText((record.limitations || [])[0])}`;
      const link = document.createElement("a");
      link.href = record.source_url;
      link.rel = "noopener noreferrer";
      link.textContent = `View source · ${escapeText(record.source_publisher)}`;
      article.append(meta, title, summary, limitation, link);
      list.append(article);
    }
  } catch (error) {
    status.textContent = "Evidence could not be loaded.";
    list.textContent = "The release data are temporarily unavailable. Please use the machine-readable evidence link in the footer.";
  }
}

loadEvidence();
