resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
}

resource "local_file" "ssh_key" {
  content  = tls_private_key.ssh_key.private_key_pem
  filename = "ssh_key.pem"
  depends_on = [tls_private_key.ssh_key]
  file_permission = "0600" # chmod 600
}