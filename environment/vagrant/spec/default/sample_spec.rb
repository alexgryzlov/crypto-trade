require 'spec_helper'


describe package('git') do
  it { should be_installed }
end


describe command('pyenv') do
  let(:disable_sudo) { true }
  its(:stderr) { should contain('pyenv 1.2.24.1') }
end



