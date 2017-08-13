## Blog usage infos

### Auto-regeneration

```
pelican --debug --autoreload -r content -o output -s pelicanconf.py
```

### Built-in server

I don't know how much better this is than the stdlib `http.server`...

```
python3 -m pelican.server 8000
```

### Generate pygments style file

```
pygmentize -S monokai -f html -a .highlight > theme/static/css/pygments.css
```
