# _Filetote_ plugin for beets

[![MIT license][license image]][license link]
[![CI][ci image]][ci link]
[![GitHub release][github image]][github link]
[![PyPI][pypi_version]][pypi_link]
[![PyPI - Python Version][pypi_python_versions]][pypi_link]

A plugin that moves non-music extra files, attachments, and artifacts during imports and
CLI file manipulation actions (`move`, `modify`, reimport, etc.) for [beets], a music
library manager (and much more!).

This plugin is supported/runs in beets `v1.6.0`.

[beets]: https://beets.io/

## Installing

### Stable

The stable version of the plugin is available from PyPI and can be installed using
`pip3`:

```sh
pip3 install beets-filetote
```

## Configuration

You will need to enable the plugin in beets' `config.yaml`:

```yaml
plugins: filetote
```

It can copy files by file extension:

```yaml
filetote:
  extensions: .cue .log
```

Or copy all non-music files:

```yaml
filetote:
  extensions: .*
```

Or copy files by filename:

```yaml
filetote:
  filenames: song.log
```

Or match based on a "pattern" ([glob pattern]):

```yaml
filetote:
  patterns:
    artworkdir:
          - "[aA]rtwork/"
```

It can look for and target "pairs" (files having the same name as a matching or "paired"
media item/track):

```yaml
filetote:
  pairing:
    enabled: true
```

You can specify pairing to happen to certain extensions, and even target/include only
paired files:

```yaml
filetote:
  pairing:
    enabled: true
    pairing_only: true
    extensions: ".lrc"
```

It can also exclude files by name:

```yaml
filetote:
  exclude: song_lyrics.nfo
```

And print what got left:

```yaml
filetote:
  print_ignored: true
```

`exclude`-d files take precedence over other matching, meaning exclude will override
other matches by either `extensions` or `filenames`.

[glob pattern]: https://docs.python.org/3/library/glob.html#module-glob

### Matching/Handling Files

In order to collect extra files and artifacts, Filetote needs to be told which types of
files it should care about. This can be done using the following:

- Extensions (`ext:`): Specify individual extensions like `.cue` or `.log`, or catch all
  non-music files with `.*`.
- Filenames (`filename:`): Match specific filenames like `cover.jpg` or organize artwork
  with `[aA]rtwork/*`.
- Patterns (`pattern:`): Use flexible glob patterns for more control, like matching all
  logs in a subfolder: `CD1/*.log`.
- Pairing: Move files with the same name as imported music items, like `.lrc` lyrics or
  album logs.

#### Extension (`ext:`)

Filename can match on the extension of the file, in a space-delimited list (i.e., a
string sequence). Take:

```yaml
filetote:
  ext: .lrc .log
```

Any file with either a `.lrc` or `.log` will match.

Use `.*` to match all file extensions.

#### Filename (`filename:`)

Filetote can match on the actual name (including extension) of the file, in a
space-delimited list (string sequence). Take this example:

```yaml
filetote:
  filenames: cover.jpg artifact.nfo
```

This will match if the filename of the given artifact or extra file matches the name
exactly as specified, in this example either `cover.jpg` or `artifact.nfo`. This will
match across any subdirectories, meaning targeting a filename in a specific subdirectory
will not work (this functionality _can_ be achieved using a `pattern`, however).

#### Pattern (`pattern:`)

Filetote can match on a given _pattern_ as specified using [glob patterns]. Paths in the
pattern are relative to the root of the importing album. Hence, if there are
subdirectories in the album's folder (for multidisc setups, for instance, e.g.,
`albumpath/CD1`), the album's path would be the base/root for the pattern (ex:
`CD1/*.jpg`). Patterns will work with or without the proceeding slash (`/`). Note:
Windows users will need to obviously use the appropriate slash (`\`).

Take, for example:

```yaml
filetote:
  patterns:
    artworkdir:
          - "[aA]rtwork/"
```

This will match all files within the given subdirectory of either `artwork/` or
`Artwork/`. Unless specified, `[aA]rtwork/` will grab all non-media files in that
subdirectory irrespective of name or extension (it is equivalent to `[aA]rtwork/*.*`).

Patterns are defined by a _name_ so that any customization for renaming can apply to the
pattern when specifying the path (ex: `pattern:artworkdir`; see the section on renaming
below).

[glob patterns]: https://docs.python.org/3/library/glob.html#module-glob

#### Pairing

Filetote can specially target related files like lyrics or logs with the same name as
music files ("paired" files). This keeps related files together, making your library
even more organized. When enabled, it will match and move those files having the same
name as a matching music file. Pairing can be configured to target only certain
extensions, such as `.lrc`.

**Note:** Pairing takes precedence over other Filetote rules like filename or patterns.

##### Pairing Example Configuration

This example configuration will grab paired `.lrc` files, along with any artwork files:

```yaml
filetote:
  pairing:
    enabled: true
    extensions: ".lrc"
  patterns:
    artworkdir:
          - "[aA]rtwork/"
```

Filetote can also be configured to _only_ target paired files, which will ignore other
Filetote configurations such as filename or patterns as described above. The following
configuration would _only_ target `.lrc` files:

```yaml
filetote:
  pairing:
    enabled: true
    pairing_only: true
    extensions: ".lrc"
```

##### Pairing Renaming

To mainting the concept of "pairs" after importing, it is strongly encouraged to set
the `path` for the paired files to use the media files new name. E.g.:

```yaml
paths:
  paired_ext:.lrc: $albumpath/$medianame_new
```

### Renaming files

Renaming works in much the same way as beets [Path Formats], though with only the below
specified fields (this will change in the future). This plugin supports the below new
path queries, which each takes a single corresponding value. These can be defined in
either the top-level `paths` section of Beet's config or in the `paths` section of
Filetote's config.

[Path Formats]: http://beets.readthedocs.org/en/stable/reference/pathformat.html

New path queries, from _most_ to _least_ specific:

- `filename:`
- `paired_ext:`
- `pattern:`
- `ext:`

Renaming has the following considerations:

- The fields available include [the standard metadata values] of the imported item
  (`$albumartist`, `$album`, `$title`, etc.), along with Filetote-specific values of:
  - `$albumpath`: the entire path of the new destination of the item/track (a useful
  shorthand for when the extra/artifact file will be moved allongside  the item/track).
  - `$old_filename`: the filename of the extra/artifact file before its renamed.
  - `$medianame_old`: the filename of the item/track triggering it, _before_ it's renamed.
  - `$medianame_new`: the filename of the item/track triggering it, _after_ it's renamed.
- The full set of [built in functions] are also supported, with the exception of
  `%aunique` - which will return an empty string.
- `filename:` path query will take precedence over `paired_ext:`, `pattern:`, and `ext:`
  if a given file qualifies for them. `paired_ext:` takes precedence over `pattern:` and
  `ext:`, but is not required. `pattern:` is higher priority than `ext:`.

[the standard metadata values]: https://beets.readthedocs.io/en/stable/reference/pathformat.html#available-values
[built in functions]: http://beets.readthedocs.org/en/stable/reference/pathformat.html#functions

Each template string uses a query syntax for each of the file extensions. For example
the following template string will be applied to `.log` files by using the `ext:` query:

```yaml
paths:
  ext:.log: $albumpath/$artist - $album
```

Or:

```yaml
filetote:
  paths:
    ext:.log: $albumpath/$artist - $album
```

This will rename a log file to:
`~/Music/Artist/2014 - Album/Artist - Album.log`

Or by using the `filename:` query:

```yaml
paths:
  filename:track.log: $albumpath/$artist - $album
```

Or:

```yaml
filetote:
  paths:
    filename:track.log: $albumpath/$artist - $album
```

This will rename the specific `track.log` log file to:
`~/Music/Artist/2014 - Album/Artist - Album.log`

> **Note:** if the rename is set and there are multiple files that qualify, only the
> first will be added to the library (new folder); other files that subsequently match
> will not be saved/renamed. To work around this, `$old_filename` can be used to help
> with adding uniqueness to the name.

### Import Operations

This plugin supports the same operations as beets:

- `copy`
- `move`
- `link` (symlink)
- `harklink`
- `reflink`

These options are mutually exclusive, and there are nuances to how beets (and thus this
plugin) behave when there multiple set. See the [beets import documentation] and [#36]
for more details.

Reimporting has an additional nuance when copying of linking files that are already in
the library, in which files will be moved rather than duplicated. This behavior in
Filetote is identical to that of beets. See the [beets reimport documentation] for more
details.

[beets import documentation]: https://beets.readthedocs.io/en/stable/reference/config.html#importer-options
[#36]: https://github.com/gtronset/beets-filetote/pull/36
[beets reimport documentation]: https://beets.readthedocs.io/en/stable/reference/cli.html#reimporting

### Other CLI Operations

Additional commands such such as `move` or `modify` will also trigger Filetote to handle
files. These commands typically work with [queries], targeting specific files that match
the supplied query. Please note that the operation executed by beets for these commands
do not use the value set in the config file under `import`, they instead are specified
as part of the CLI command.

[queries]: https://beets.readthedocs.io/en/stable/reference/query.html

### Examples of `config.yaml`

```yaml
plugins: filetote

paths:
  default: $albumartist/$year - $album/$track - $title
  singleton: Singletons/$artist - $title
  ext:.log: $albumpath/$artist - $album
  ext:.cue: $albumpath/$artist - $album
  paired_ext:.lrc: $albumpath/$medianame_old
  filename:cover.jpg: $albumpath/cover

filetote:
  extensions: .cue .log .jpg
  filename: "cover.jpg"
  pairing:
    enabled: true
    extensions: ".lrc"
  print_ignored: true
```

Or:

```yaml
plugins: filetote

paths:
  default: $albumartist/$year - $album/$track - $title
  singleton: Singletons/$artist - $title

filetote:
  extensions: .cue
  patterns:
    artworkdir:
          - "[sS]cans/"
          - "[aA]rtwork/"
  pairing:
    enabled: true
    extensions: ".lrc"
  paths:
    pattern:artworkdir: $albumpath/artwork
    paired_ext:.lrc: $albumpath/$medianame_old
    filename:cover.jpg: $albumpath/cover  
```

## Multi-Disc and Nested Import Directories

beets imports multi-disc albums as a single unit ([see beets documentation]). By
default, this results in the media importing to a single directory in the library.
Artifacts and extra files in the initial subdirectories will brought by Filetote to the
destination of the file's they're near, resulting in them landing where one would expect.
Because of this, the files will also be moved by Filetote to any specified subdirectory
in the library if the path definition creates "Disc N" subfolders
[as described in the beets documentation].

In short, artifacts and extra files in these scenarios should simply just move/copy as
expected.

[see beets documentation]: https://beets.readthedocs.io/en/stable/faq.html#import-a-multi-disc-album
[as described in the beets documentation]: https://beets.readthedocs.io/en/stable/faq.html#create-disc-n-directories-for-multi-disc-albums

## Why Filetote and Not Other Plugins?

Filetote serves the same core purpose as the [`copyfilertifacts` plugin] and the
[`extrafiles` plugin], however both have lacked in maintenance over the last few years.
There are outstanding bugs in each (though `copyfilertifacts` has seen some recent
activity resolving some). In addition, each are lacking in certain features and
abilities, such as hardlink/reflink support, "paired" file handling, and extending
renaming options. What's more, significant focus has been provided to Filetote around
Python3 conventions, linting, and typing in order to promote healthier code and easier
maintenance.

Filetote strives to encompass all functionality that _both_ `copyfilertifacts`
and `extrafiles` provide, and then some!

[`copyfilertifacts` plugin]: https://github.com/adammillerio/beets-copyartifacts
[`extrafiles` plugin]: https://github.com/Holzhaus/beets-extrafiles

### Migrating from `copyfilertifacts`

Filetote can be configured using nearly identical configuration as `copyfilertifacts`,
simply replacing the name of the plugin in its configuration settings. **There is one
change that's needed if all extensions are desired, as Filetote does not grab all
extensions by default (as `copyfilertifacts` does).** To accommodate, simply explicitly
state all extension using `.*`:

```yaml
filetote:
    extensions: .*
```

Otherwise, simply replacing the name in the config section will work. For example:

```yaml
copyartifacts:
    extensions: .cue .log
```

Would become:

```yaml
filetote:
    extensions: .cue .log
```

Path definitions can also be specified in the way that `copyfileartifacts` does,
alongside other path definitions for beets. E.g.:

```yaml
paths:
    ext:log: $albumpath/$artist - $album
```

### Migrating from `extrafiles`

Filetote can be configured using nearly identical configuration as `extrafiles`, simply
replacing the name of the plugin in its configuration settings. For example:

```yaml
extrafiles:
    patterns:
        all: "*.*"
```

Would become:

```yaml
filetote:
    patterns:
        all: "*.*"
```

Path definitions can also be specified in the way that `extrafiles` does, e.g.:

```yaml
filetote:
    patterns:
        artworkdir:
          - '[sS]cans/'
          - '[aA]rtwork/'
    paths:
        artworkdir: $albumpath/artwork
```

## Version Upgrade Instructions

Certain versoins require changes to configurations as upgrades occur. Please see below
for specific steps for each version.

### `0.4.0`

#### Default extensions is now `None`

As of version `0.4.0`, Filetote no longer set the default for `extensions` to `.*`.
Instead, setting Filetote to collect all extensions needs to be explicitly defined, e.g.:

```yaml
filetote:
    extensions: .*
```

#### Pairing Config Changes

`pairing` has been converted from a boolean to an object with other like-config. Take
the following config:

```yaml
filetote:
  pairing: true
  pairing_only: false
```

These will both now be represented as individual settings within `pairing`:

```yaml
filetote:
  pairing:
    enabled: true
    pairing_only: false
    extensions: ".lrc"
```

Both remain optional and both default to `false`.

## Development

The development version can now be installed with [Poetry], a Python dependency manager
that provides dependency isolation, reproducibility, and streamlined packaging to PyPI.

**1. Install Poetry:**

```sh
python3 -m pip install poetry
```

**2. Clone the repository and install the plugin:**

```sh
git clone https://github.com/gtronset/beets-filetote.git
cd beets-filetote
poetry install
```

**3. Update the config.yaml to utilize the plugin:**

```yaml
pluginpath:
  - /path/to.../beets-filetote/beetsplug
```

**Docker:**

A Docker Compose configuration is available for running the plugin in a controlled
environment. See the `.dev-docker/docker-compose.yml` file for details.

[Poetry]: https://python-poetry.org/

## Thanks

This plugin originated as a hard fork from [beets-copyartifacts (copyartifacts3)].

Thank you to the original work done by Sami Barakat, Adrian Sampson, along with the
larger [beets](http://beets.io) community.

Please report any issues you may have and feel free to contribute.

[beets-copyartifacts (copyartifacts3)]: https://github.com/adammillerio/beets-copyartifacts

## License

Copyright (c) 2022 Gavin Tronset

Licensed under the [MIT license][license link].

[license image]: https://img.shields.io/badge/License-MIT-blue.svg
[license link]: https://github.com/gtronset/beets-filetote/blob/main/LICENSE
[ci image]: https://github.com/gtronset/beets-filetote/actions/workflows/tox.yml/badge.svg
[ci link]: https://github.com/gtronset/beets-filetote/actions/workflows/tox.yml
[github image]: https://img.shields.io/github/release/gtronset/beets-filetote.svg
[github link]: https://github.com/gtronset/beets-filetote/releases
[pypi_version]: https://img.shields.io/pypi/v/beets-filetote
[pypi_link]: https://pypi.org/project/beets-filetote/
[pypi_python_versions]: https://img.shields.io/pypi/pyversions/beets-filetote
