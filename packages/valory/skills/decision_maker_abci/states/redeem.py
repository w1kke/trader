# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2023 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the redeem state of the decision-making abci app."""

from enum import Enum
from typing import Optional, Tuple, Type, cast

from packages.valory.skills.abstract_round_abci.base import (
    BaseSynchronizedData,
    get_name,
)
from packages.valory.skills.decision_maker_abci.payloads import (
    MultisigTxPayload,
    RedeemPayload,
)
from packages.valory.skills.decision_maker_abci.states.base import (
    Event,
    SynchronizedData,
    TxPreparationRound,
)


class RedeemRound(TxPreparationRound):
    """A round in which the agents prepare a tx to redeem the winnings."""

    payload_class: Type[MultisigTxPayload] = RedeemPayload
    selection_key = TxPreparationRound.selection_key + (
        get_name(SynchronizedData.policy),
        get_name(SynchronizedData.utilized_tools),
        get_name(SynchronizedData.redeemed_condition_ids),
        get_name(SynchronizedData.payout_so_far),
    )
    none_event = Event.NO_REDEEMING

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        res = super().end_block()
        if res is None:
            return None

        synced_data, event = cast(Tuple[SynchronizedData, Enum], res)

        if synced_data.period_count == 0:
            # necessary for persisted keys to function properly and not raise an exception when the first period ends
            update = {
                db_key: getattr(synced_data, db_key)
                for db_key in RedeemRound.selection_key
            }
            synced_data.db.update(**update)

        return synced_data, event
