output "vm_ip" {
  value = google_compute_instance.fog-computing.network_interface.0.access_config.0.nat_ip
}

resource "local_file" "ip_file" {
  content  = google_compute_instance.fog-computing.network_interface.0.access_config.0.nat_ip
  filename = "ip.txt"
  file_permission = "0600" # chmod 600
}
