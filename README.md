# win0168-sls-webcrawl

This is serverless project which uses headless chrome and selenium on container image on AMS Lambda

This image goes with these versions.

- Python 3.8
- serverless-chrome v1.0.0-55
  - chromium 69.0.3497.81 (stable channel) for amazonlinux:2017.03
- chromedriver 2.43
- selenium 3.141.0 (latest)

### Running the program

- Define Region, Bucket Name (name equals to Target Route 53 Domain), and Image Version, in serverless.yaml
- Define Bucket Name in Dockerfile

```bash
$ sls deploy --region $YOUR_REGION
$ sls invoke -f server --region $YOUR_REGION
```

### Contribution

Run latest Chrome but having difficulties.
Try upgrading Chrome and Selenium if available.

### Reference

[pythonista-chromeless](https://github.com/umihico/pythonista-chromeless)
