#!/bin/bash
pushd docs
rm -Rf _build
make html
popd
mkdir -p tcd/public/docs
rm -Rf tcd/public/docs/*
cp -R docs/_build/html/* tcd/public/docs
