require 'spec_helper'


describe package('git') do
  it { should be_installed }
end

describe package('flake8') do
  it { should be_installed.by('pip').with_version('3.8.3') }
end

describe package('mypy') do
  it { should be_installed.by('pip').with_version('0.782') }
end

describe package('requests') do
  it { should be_installed.by('pip').with_version('2.24.0') }
end

describe package('numpy') do
  it { should be_installed.by('pip').with_version('1.19.1') }
end

describe package('pytest') do
  it { should be_installed.by('pip').with_version('6.0.1') }
end

describe package('pandas') do
  it { should be_installed.by('pip').with_version('1.1.0') }
end

describe package('python-dateutil') do
  it { should be_installed.by('pip').with_version('2.8.1') }
end

describe package('plotly') do
  it { should be_installed.by('pip').with_version('4.14.3') }
end

describe package('ccxt') do
  it { should be_installed.by('pip').with_version('1.43.72') }
end

describe package('retry') do
  it { should be_installed.by('pip').with_version('0.9.2') }
end

describe package('scikit-learn') do
  it { should be_installed.by('pip').with_version('0.24.1') }
end

describe package('dash') do
  it { should be_installed.by('pip').with_version('1.19.0') }
end

describe package('mypy-extensions') do
  it { should be_installed.by('pip').with_version('0.4.3') }
end

describe package('varname') do
  it { should be_installed.by('pip').with_version('0.6.3') }
end

describe package('python-dotenv') do
  it { should be_installed.by('pip').with_version('0.15.0') }
end




