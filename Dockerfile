FROM pytorch/pytorch:1.9.0-cuda10.2-cudnn7-runtime

ARG APT_INSTALL="apt-get install -y --no-install-recommends"

# should be: drwxrwxrwt
# otherwise: Couldn't create temporary file /tmp/apt.conf.XXXXXX for passing config to apt-key
RUN chmod 1777 /tmp
RUN apt-get update && apt-get install -y python3-pip git vim unzip

## Locale
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONPATH /root/medical-crossing/

## Setting up the workhorse
ADD ./ /root/medical-crossing
WORKDIR /root/medical-crossing
RUN pip install -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt')"

#RUN rm -rf sapbert SapBert
#RUN git clone https://github.com/cambridgeltl/sapbert.git
#RUN cp data/vocabs/umls* sapbert/evaluation/xl_bel/
#RUN mv sapbert SapBert

RUN rm -rf Fair-Evaluation-BERT
RUN git clone https://github.com/alexeyev/Fair-Evaluation-BERT

# should we use a small one?
# may consider pre-downloading?
RUN python -m pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_sm-0.4.0.tar.gz || \
    python -m pip install en_core_sci_sm-0.4.0.tar.gz
RUN python -m pip install --upgrade transformers
WORKDIR /root/medical_crossing/