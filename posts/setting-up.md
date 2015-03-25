.. title: Setting Up
.. date: 2014-08-16
.. slug: setting-up


I needed to clean up my dev environment, so these are my notes for getting my mac running.
Mostly from memory and mostly for my future self, so be warned.

### Package Management

Use homebrew. If you can get by with the Xcode Command Line Tools, do that.

```
xcode-select install
```

Some applications (like MacVim) require a full installatoin of Xcode, which you can get off the App Store.

Once you have that, get homebrew with

```
ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
```

### Shell

I use fish-shell.

```
brew install fish
```

Here's my `config.fish`.
I use virtualfish, which I keep in `~/.config/fish/virtualfish.`

### Python

I try to not mess with the System python.
So get the homebrew python setup as early as possible.

```
brew install python
brew install python3

pip intsall virtualenv
pip install virtualenvwrapper
```

You should *always* use virtualenvs.
My virtualenv home is in `~/Envs/`.

### Scientific Python

For the numpy stack.
May need some C libraries.

```
brew install libxml2
brew install libxlst
brew install hdf5
brew install zeromq
```

Now for the python stuff.

```shell
workon <virtualenv>
cdsitepackages

pip install numpy
pip install scipy
pip install cython pytz python-dateutil
pip install numexpr bottleneck 
pip install lxml beautifulsoup4 tables xlrd xlwt html5lib nose
pip install jinja2 pyzmq

git clone https://github.com/pydata/pandas
git clone https://github.com/statsmodels/statsmodels
git clone https://github.com/matplotlib/matplotlib
git clone https://github.com/ipython/ipython
```

Then do the usual `cd`ing into those git repos. For pandas
I build the C extensions inplace

```
python setup.py build_ext --inplace; and python setup.py install
```

For IPython make sure to init and update their submodules with
`python setup.py submodule`.

### Blog

Using the pelican static site generator.

```
vf new blog
pip install pelican markdown
git clone https://github.com/TomAugspurger/blog-source.git
```


### Editor

I'm slowly switching over to Vim/MacVim.

```
brew unlink python  # I'll explain later
brew install vim --override-system-vim
brew install macvim
```

Manage plugins with Vundle.

I had some trouble with YCM picking up the wrong python and crashing.
Make sure to set the path in your vimrc. For some reason, MacVim compiled
with the system python rather than homebrew (which came first on my path),
so I directed YCM to it.


```
cd ~/.vim/bundle/YouCompleteMe/
./install.sh
brew link python
```

Then in your .vimrc point YCM to the System python,
the one macvim complied agains.

```
let g:ycm_path_to_python_interpreter = '/usr/bin/python'
```

I only got it working when I first `brew unlink python` before brewing
macvim. So the order should be

```
brew unlink python
brew install macvim
./install.sh  # in ~/.vim/bundle/YouCompleteMe
brew link python
```

### Haskell

I tried out [ghcformacosx](http://ghcformacosx.github.io);
we'll see how well it goes.
I unzipped the app to `/Applications` and made a symlink to it
so that I don't have to chagne my path every time ghc is updated.

```
ln -s /Applications/ghc-7.8.3.app /Applications/ghc.app
```

Here's my `ghci.conf` and my `~/.cabal/config`.
I'm experiementing with always using cabal sandboxes.
However, I'd like hdevtools and such to always be available for editing.
There's probably a way to share those across libraries, so I could put
them on their own sandbox, but for now I'll just install them globally.

I had to manually install happy and haskell-src-exts. 

```
cabal update
cabal install cabal-install

cabal install happy
cabal install haskell-src-ext-1.15.0.1
```


```
cabal install hdevtools ghc-mode hlint
```

I'm also trying out lushtags, which I had to [fork](https://github.com/TomAugspurger/lushtags)
to adjust the cabal requirements.

Install with

```shell
cabal configure
cabal build
cabal install
```

Then uncomment the line `-- require-sandbox: True` in your `~/.cabal/config`.

