Vagrant.configure("2") do |config|

  config.vm.define :centos65 do |centos65|
    centos65.vm.box = "opscode-centos-6.5"
    centos65.vm.box_url = "https://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_centos-6.5_chef-provisionerless.box"
    centos65.vm.hostname = "centos65"
  end

  config.vm.define :ubuntu1204 do |ubuntu1204|
    #ubuntu1204.vm.box = 'opscode-ubuntu-12.04'
    #ubuntu1204.vm.box_url = 'http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_ubuntu-12.04_chef-provisionerless.box'
    ubuntu1204.vm.box = 'ubuntu-12.04'
    ubuntu1204.vm.box_url = 'http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-amd64-vagrant-disk1.box'
    ubuntu1204.vm.hostname = "ubuntu1204"
  end

  config.vm.define :debian7 do |debian7|
    debian7.vm.box = 'opscode-debian-7.2.0'
    debian7.vm.box_url = 'http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_debian-7.2.0_chef-provisionerless.box'
    debian7.vm.hostname = "debian7"
  end

  config.vm.define :fedora20 do |fedora20|
    fedora20.vm.box = 'opscode-fedora-20'
    fedora20.vm.box_url = 'http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_fedora-20_chef-provisionerless.box'
    fedora20.vm.hostname = "fedora20"
  end

  config.vm.define :ubuntu1310 do |ubuntu1310|
    ubuntu1310.vm.box = 'opscode-ubuntu-13.10'
    ubuntu1310.vm.box_url = 'http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_ubuntu-13.10_chef-provisionerless.box'
    ubuntu1310.vm.hostname = "ubuntu1310"
  end

  config.vm.provider "virtualbox" do |v|
    v.customize [ "modifyvm", :id, "--cpuexecutioncap", "50", "--memory", 512 ]
  end

end
