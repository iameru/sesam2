vm_name = "sesam2-vm"

provision_script = <<~SCRIPT

sudo apt update
sudo apt install -y python3-pip pipx
pipx install poetry
sudo apt install -y npm

SCRIPT

Vagrant.configure("2") do |config|
  config.vm.define vm_name
  config.vm.hostname = vm_name
  config.vm.box = "generic/debian12"
  config.vm.synced_folder "./sesam2-frontend", "/home/vagrant/frontend", type: "nfs", nfs_version: 4, nfs_udp: false, mount_options: ['rw']
  config.vm.synced_folder "./sesam2-backend", "/home/vagrant/backend", type: "nfs", nfs_version: 4, nfs_udp: false, mount_options: ['ro']
  config.vm.network "forwarded_port", guest: 8000, host: 8000 # backend
  config.vm.network "forwarded_port", guest: 5000, host: 5000 # frontend
  config.vm.provision "shell", inline: provision_script # untested currently
end
