# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"
  config.vm.share_folder "v-app", "/usr/local/src/geofu", "./"
  config.vm.provision :shell, :path => "scripts/provision.sh"
end
