resource "google_compute_firewall" "allow-tcp" {
  name    = "allow-tcp"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["4411"]
  }

  # allow ssh
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["replay-server"]
}
