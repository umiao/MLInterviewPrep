-- T-P0-199 seed + retrofit archive (Pinterest SDs + 3 docs + link fix in docs 47,36)
-- Generated 2026-04-14. Idempotent-by-slug / title.

-- SD: slug=pinterest-ad-ctr display_order=100 title=Pinterest ML System Design: Ad CTR Prediction
-- SD: slug=pinterest-embeddings display_order=101 title=Pinterest ML System Design: User & Item (Pin) Embeddings
-- SD: slug=pinterest-chatbot-pins display_order=102 title=Pinterest ML System Design: Personalized Chat Bot Recommending Pins
-- SD: slug=pinterest-pin-ranking display_order=103 title=Pinterest ML System Design: Pin Ranking for Home/Topic Feed
-- SD: slug=pinterest-pins-search display_order=104 title=Pinterest ML System Design: Pins Search Engine
-- SD: slug=pinterest-notification-reco display_order=105 title=Pinterest ML System Design: Notification Recommendation
-- SD: slug=pinterest-catalog-bulk-update display_order=106 title=Pinterest SD: Catalog Bulk Update (500M records, S3 + Async Fan-out)
-- DOC: id=48 company_id=29 title=Pinterest BQ Question Map
-- DOC: id=49 company_id=29 title=Pinterest LC Investigation: Restaurant Intervals
-- DOC: id=50 company_id=5 title=Uber Phone Screen Prep

-- Re-apply via: python scripts/seed_pinterest_sd.py && python scripts/fix_placeholder_md_links.py