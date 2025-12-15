from fastapi.testclient import TestClient


def test_read_trips_returns_list(client: TestClient):
    resp = client.get("/api/v1/trips/")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    if body:
        assert "slug" in body[0]
        assert "is_active" in body[0]
        assert "title" in body[0]


def test_create_trip(client: TestClient):
    resp = client.post(
        "/api/v1/trips/",
        data={
            "title": "Bangkok Trip",
            "is_active": "true"
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Bangkok Trip"
    assert "slug" in body
    # slug saved for later tests by returning it from this helper or re‑querying


def test_trip_crud_flow(client: TestClient):
    # Create
    create = client.post(
        "/api/v1/trips/",
        data={
            "title": "Yangon Trip",
            "is_active": "true"
        },
    )
    assert create.status_code == 200
    trip = create.json()
    slug = trip["slug"]

    # Create with same name variants
    create_conflict_400 = client.post(
        "/api/v1/trips/",
        data={
            "title": "Yangon Trip",
        },
    )
    assert create_conflict_400.status_code == 400

    create_conflict_different_case_400 = client.post(
        "/api/v1/trips/",
        data={
            "title": "YANGON Trip",
        },
    )
    assert create_conflict_different_case_400.status_code == 400

    create_conflict_whitespace_400 = client.post(
        "/api/v1/trips/",
        data={
            "title": " Yangon Trip ",
        },
    )
    assert create_conflict_whitespace_400.status_code == 400

    # Read single
    read = client.get(f"/api/v1/trips/{slug}")
    assert read.status_code == 200
    assert read.json()["slug"] == slug
    assert read.json()["is_active"] is True

    # Read all
    all_trips = client.get("/api/v1/trips/")
    assert all_trips.status_code == 200
    trips_list = all_trips.json()
    assert any(t["slug"] == slug for t in trips_list)

    # Update
    update = client.put(
        f"/api/v1/trips/{slug}",
        data={
            "title": "Updated Yangon Trip"
        },
    )
    assert update.status_code == 200
    updated = update.json()
    assert updated["title"] == "Updated Yangon Trip"
    updated_slug = updated["slug"]
    assert updated_slug != slug
    assert updated_slug == "updated-yangon-trip"

    # Delete
    delete = client.delete(f"/api/v1/trips/{updated_slug}")
    assert delete.status_code == 204

    # Ensure gone
    read_again = client.get(f"/api/v1/trips/{slug}")
    assert read_again.status_code == 404
    # Ensure trip with old slug also gone
    read_again = client.get(f"/api/v1/trips/{updated_slug}")
    assert read_again.status_code == 404


def test_create_trip_defaults_inactive(client: TestClient):
    resp = client.post(
        "/api/v1/trips/",
        data={"title": "Default Active Test"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Default Active Test"
    assert body["is_active"] is False


def test_only_one_active_trip(client: TestClient):
    # Trip A inactive
    a = client.post(
        "/api/v1/trips/",
        data={"title": "Trip A"},
    )
    assert a.status_code == 200
    trip_a = a.json()

    # Trip B active
    b = client.post(
        "/api/v1/trips/",
        data={"title": "Trip B", "is_active": "true"},
    )
    assert b.status_code == 200
    trip_b = b.json()
    assert trip_b["is_active"] is True

    update_a = client.put(
        f"/api/v1/trips/{trip_a['slug']}",
        data={"title": trip_a["title"], "is_active": "true"},
    )
    assert update_a.status_code == 200
    updated_a = update_a.json()
    assert updated_a["is_active"] is True

    # Re-read B and ensure it is now inactive
    read_b = client.get(f"/api/v1/trips/{trip_b['slug']}")
    assert read_b.status_code == 200
    assert read_b.json()["is_active"] is False

