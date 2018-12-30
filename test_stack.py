from rasa_core.policies import FallbackPolicy, KerasPolicy, MemoizationPolicy
from rasa_core.agent import Agent

from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu import config

from rasa_core.trackers import DialogueStateTracker
from rasa_core.domain import Domain
from rasa_core.dispatcher import Dispatcher
from rasa_core.channels import CollectingOutputChannel
from rasa_core.nlg import TemplatedNaturalLanguageGenerator
from actions import ActionJoke
import uuid


def test_nlu_interpreter():
    training_data = load_data("data/nlu_data.md")
    trainer = Trainer(config.load("nlu_config.yml"))
    interpreter = trainer.train(training_data)
    test_interpreter_dir = trainer.persist("./models/nlu", fixed_model_name="test")

    assert interpreter.parse('hello') is not None
    assert test_interpreter_dir


def test_agent_and_persist():
    agent = Agent('domain.yml', policies=[MemoizationPolicy(), KerasPolicy(epochs=2), FallbackPolicy()])
    training_data = agent.load_data('data/stories.md')
    agent.train(training_data, validation_split=0.0)
    agent.persist('models/dialogue')

    loaded = Agent.load('models/dialogue')

    assert agent.handle_text('/greet') is not None
    assert loaded.domain.action_names == agent.domain.action_names
    assert loaded.domain.intents == agent.domain.intents
    assert loaded.domain.entities == agent.domain.entities
    assert loaded.domain.templates == agent.domain.templates


def test_action():
    domain = Domain.load('domain.yml')
    nlg = TemplatedNaturalLanguageGenerator(domain.templates)
    dispatcher = Dispatcher("my-sender", CollectingOutputChannel(), nlg)
    uid = str(uuid.uuid1())
    tracker = DialogueStateTracker(uid, domain.slots)

    action = ActionJoke()
    action.run(dispatcher, tracker, domain)

    assert dispatcher.output_channel.latest_output() is not None
