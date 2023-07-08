resource "google_compute_instance" "fog-computing" {
  name         = "fog-computing"
  machine_type = "e2-standard-2"
  tags         = ["replay-server"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata = {
    ssh-keys       = "ubuntu:${tls_private_key.ssh_key.public_key_openssh}"
    startup-script = "${file("setup.sh")}"
  }

  connection {
    user        = "ubuntu"
    host        = self.network_interface.0.access_config.0.nat_ip
    private_key = tls_private_key.ssh_key.private_key_pem
  }

  provisioner "file" {
    source      = "../../fc-practice/"
    destination = "/home/ubuntu"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo docker compose -f /home/ubuntu/docker-compose.cloud.yml up -d"
    ]
  }
}
