.. title: Organizing Papers
.. date: 2014-02-13 12:00
.. slug: Organizing Papers
.. category: scripts
.. tags: python, scripts

As a graduate student, you read a lot of journal articles... *a lot*.
With the material in the articles being as difficult as it is, I didn't want to worry about organizing everything as well.
That's why I wrote [this script](https://gist.github.com/TomAugspurger/8976751) to help (I may have also been procrastinating from studying for my qualifiers). This was one of my earliest little projects, so I'm not claiming that this is the best way to do anything.

My goal was to have a central repository of papers that was organized by an author's last name. Under each author's name would go all of their papers I had read or planned to read.
I needed it to be portable so that I could access any paper from my computer or iPad, so Dropbox was a necessity. I also needed to organize the papers by subject. I wanted to easily get to all the papers on Asset Pricing, without having to go through each of the authors separately.
[Symbolic links](http://en.wikipedia.org/wiki/Symbolic_link) were a natural solution to my problem.
A canonical copy of each paper would be stored under `/Drobox/Papers/<author name>`, and I could refer that paper from `/Macro/Asset Pricing/` with a symbolic link. Symbolic links avoid the problem of having multiple copies of the same paper. Any highlighting or notes I make on a paper is automatically spread to anywhere that paper is linked from.

```python
import os
import re
import sys
import subprocess

import pathlib


class Parser(object):
    def __init__(self, path,
                 repo=pathlib.PosixPath('/Users/tom/Economics/Papers')):
        self.repo = repo
        self.path = self.path_parse(path)
        self.exists = self.check_existance(self.path)
        self.is_full = self.check_full(path)
        self.check_type(self.path)
        self.added = []

    def path_parse(self, path):
        """Ensures a common point of entry to the functions.
        Returns a pathlib.PosixPath object
        """
        if not isinstance(path, pathlib.PosixPath):
            path = pathlib.PosixPath(path)
            return path
        else:
            return path

    def check_existance(self, path):
        if not path.exists():
            raise OSError('The supplied path does not exist.')
        else:
            return True

    def check_type(self, path):
        if path.is_dir():
            self.is_dir = True
            self.is_file = False
        else:
            self.is_file = True
            self.is_dir = False

    def check_full(self, path):
        if path.parent().as_posix() in path.as_posix():
            return True

    def parser(self, f):
        """The parsing logic to find authors and paper name from a file.
        f is a full path.
        """
        try:
            file_name = f.parts[-1]
            self.file_name = file_name
            r = re.compile(r' \([\d-]{0,4}\)')
            sep_authors = re.compile(r' & |, | and')

            all_authors, paper = re.split(r, file_name)
            paper = paper.lstrip(' - ')
            authors = re.split(sep_authors, all_authors)
            authors = [author.strip('& ' or 'and ') for author in authors]
            self.authors, self.paper = authors, paper
            return (authors, paper)
        except:
            print('Missed on {}'.format(file_name))

    def make_dir(self, authors):
        repo = self.repo
        for author in authors:
            try:
                os.mkdir(repo[author].as_posix())
            except OSError:
                pass

    def copy_and_link(self, authors, f, replace=True):
        repo = self.repo
        file_name = f.parts[-1]
        for author in authors:
            if author == authors[0]:
                try:
                    subprocess.call(["cp", f.as_posix(),
                                    repo[author].as_posix()])
                    success = True
                except:
                    success = False
            else:
                subprocess.call(["ln", "-s",
                                repo[authors[0]][file_name].as_posix(),
                                repo[author].as_posix()])
                success = True
            if replace and author == authors[0] and success:
                try:
                    f.unlink()
                    subprocess.call(["ln", "-s",
                                    repo[authors[0]][file_name].as_posix(),
                                    f.parts[:-1].as_posix()])
                except:
                    raise OSError

    def main(self, f):
        authors, paper = self.parser(f)
        self.make_dir(authors)
        self.copy_and_link(authors, f)

    def run(self):
        if self.exists and self.is_full:
            if self.is_dir:
                for f in self.path:
                    if f.parts[-1][0] == '.' or f.is_symlink():
                        pass
                    else:
                        try:
                            self.main(f)
                            self.added.append(f)
                        except:
                            print('Failed on %s' % str(f))
            else:
                self.main(self.path)
                self.added.append(self.path)
            for item in self.added:
                print(item.parts[-1])

if __name__ == "__main__":
    p = pathlib.PosixPath(sys.argv[1])
    try:
        repo = pathlib.PosixPath(sys.argv[2])
    except:
        repo = pathlib.PosixPath('/Users/tom/Economics/Papers')
    print(p)
    obj = Parser(p, repo)
    obj.run()

```

The script takes two arguments, the folder to work on and the folder to store the results (defaults to `/Users/tom/Economics/Papers`). Already a could things jump out that I should update. If I ever wanted to add more sophisticated command line arguments I would want to switch to something like [`argparse`](http://docs.python.org/dev/library/argparse.html). I also shouldn't have something like `/Users/tom` anywhere. This kills portability since it's specific to my computer (use `os.path.expanduser('~')` instead).

I create a `Parser` which finds every paper in the directory given by the first argument. I had to settle on a standard naming for my papers. I chose `Author1, Author2, ... and AuthorN (YYYY) - Paper Title`. Whenever `Parser` find that pattern, it splits off the Authors from the title of the paper, and stores the location of the file.

After doing this for each paper in the directory, it's time to copy and link the files.

```python
for author in authors:
    if author == authors[0]:
        try:
            subprocess.call(["cp", f.as_posix(),
                            repo[author].as_posix()])
            success = True
        except:
            success = False
    else:
        subprocess.call(["ln", "-s",
                        repo[authors[0]][file_name].as_posix(),
                        repo[author].as_posix()])
        success = True
```

Since I just one one actual copy of the paper on file, I only copy the paper to the first author's sub-folder. Thats the `if author == authors[0]`. Every other author just links to the copy stored in the first author's folder. The wiser me of today would use something like [`shutil`](http://docs.python.org/2/library/shutil.html) to copy the files instead of `subprocess`, but I was still new to python.

<iframe src="https://www.flickr.com/photos/81581328@N02/12501636805/player/3eb021f38a" height="509" width="800"  frameborder="0" allowfullscreen webkitallowfullscreen mozallowfullscreen oallowfullscreen msallowfullscreen></iframe>

The biggest drawback is that I can't differentiate multiple authors with the same last name that well. I need to edit the original names to include the first initials (`C. Romer and D. Romer (2010)`). But overall I'm pleased with the results.
