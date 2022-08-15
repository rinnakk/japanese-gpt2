# coding=utf-8
# Copyright 2021 rinna Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os

import torch
from task.pretrain_roberta.modeling_roberta_japanese import RobertaJapaneseForMaskedLM
from transformers import PretrainedConfig
from task.pretrain_roberta.modeling_tf_roberta_japanese import TFRobertaJapaneseForMaskedLM
from task.pretrain_roberta.tokenization_roberta_japanese import RobertaJapaneseTokenizer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint_path", help="path to saved checkpoint file", type=str, required=True)
    parser.add_argument("--save_dir", help="path to saved checkpoint file", type=str, default="../data/huggingface_model/roberta-ja-base")
    parser.add_argument("--model_config_filepath", type=str, default="model/roberta-ja-base-config.json")
    args = parser.parse_args()

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)

    RobertaJapaneseTokenizer.register_for_auto_class()
    RobertaJapaneseForMaskedLM.register_for_auto_class("AutoModelForMaskedLM")
    # TFRobertaJapaneseForMaskedLM.register_for_auto_class("TFAutoModelForMaskedLM")
    # Waiting for: https://github.com/huggingface/transformers/pull/18607

    tokenizer = RobertaJapaneseTokenizer(
        vocab_file="../data/tokenizer/google_sp.model",
        bos_token="<s>",
        eos_token="</s>",
        unk_token="<unk>",
        pad_token="[PAD]",
        cls_token="[CLS]",
        sep_token="[SEP]",
        mask_token="[MASK]",
        extra_ids=0,
        additional_special_tokens=(),
        do_lower_case=True,
        workaround_for_add_dummy_prefix=True
    )
    tokenizer.save_pretrained(args.save_dir)
    tokenizer.save_vocabulary(args.save_dir)

    checkpoint = torch.load(args.checkpoint_path, map_location="cpu")

    model_config = PretrainedConfig.from_json_file(args.model_config_filepath)
    model = RobertaJapaneseForMaskedLM(model_config)
    model.load_state_dict(checkpoint["model"])
    model.save_pretrained(args.save_dir)

    tf_model = TFRobertaJapaneseForMaskedLM.from_pretrained(f"{args.save_dir}", from_pt=True)
    tf_model.save_pretrained(args.save_dir)
