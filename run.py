#!/usr/bin/env python

# -*- coding: utf-8 -*-
from patientMatcher import create_app

app = create_app()
app.run(port=9020)
