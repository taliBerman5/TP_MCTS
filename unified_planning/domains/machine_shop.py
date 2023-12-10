import itertools

import unified_planning as up
from unified_planning.domains import Domain
from unified_planning.shortcuts import *


class Machine_Shop(Domain):
    def __init__(self, kind, deadline, object_amount, garbage_amount=None):
        Domain.__init__(self, 'machine_shop', kind)
        assert object_amount > 1
        self.object_amount = object_amount
        self.user_types()
        self.objects()
        self.fluents()
        self.actions()
        self.set_initial_state()
        self.add_goal(deadline)

    def user_types(self):
        Piece = UserType('Piece')
        Machine = UserType('Machine')
        self.userTypes = dict(Piece=Piece, Machine=Machine)

    def objects(self):
        """ Init piece """
        piece_names = ['x'+str(i) for i in range(self.object_amount)]
        pieces = [unified_planning.model.Object(p, self.userTypes['Piece']) for p in piece_names]
        self.problem.add_objects(pieces)

        """ Init machine """
        machine_names = ['m'+str(i) for i in range(self.object_amount)]
        machines = [unified_planning.model.Object(m, self.userTypes['Machine']) for m in machine_names]
        self.problem.add_objects(machines)

    def fluents(self):
        shaped = unified_planning.model.Fluent('shaped', BoolType(), p=self.userTypes['Piece'])
        self.problem.add_fluent(shaped, default_initial_value=False)

        painted = unified_planning.model.Fluent('painted', BoolType(), p=self.userTypes['Piece'])
        self.problem.add_fluent(painted, default_initial_value=False)

        smooth = unified_planning.model.Fluent('smooth', BoolType(), p=self.userTypes['Piece'])
        self.problem.add_fluent(smooth, default_initial_value=False)

        polished = unified_planning.model.Fluent('polished', BoolType(), p=self.userTypes['Piece'])
        self.problem.add_fluent(polished, default_initial_value=False)

        canpolpaint = unified_planning.model.Fluent('canpolpaint', BoolType(), m=self.userTypes['Machine'])
        self.problem.add_fluent(canpolpaint, default_initial_value=False)

        canlatroll = unified_planning.model.Fluent('canlatroll', BoolType(), m=self.userTypes['Machine'])
        self.problem.add_fluent(canlatroll, default_initial_value=False)

        cangrind = unified_planning.model.Fluent('cangrind', BoolType(), m=self.userTypes['Machine'])
        self.problem.add_fluent(cangrind, default_initial_value=False)

        hasimmersion = unified_planning.model.Fluent('hasimmersion', BoolType(), m=self.userTypes['Machine'])
        self.problem.add_fluent(hasimmersion, default_initial_value=False)

        free = unified_planning.model.Fluent('free', BoolType(), m=self.userTypes['Machine'])
        self.problem.add_fluent(free, default_initial_value=False)

        at = unified_planning.model.Fluent('at', BoolType(), p=self.userTypes['Piece'], m=self.userTypes['Machine'])
        self.problem.add_fluent(at, default_initial_value=False)

        on = unified_planning.model.Fluent('on', BoolType(), p=self.userTypes['Piece'], m=self.userTypes['Machine'])
        self.problem.add_fluent(on, default_initial_value=False)

    def set_initial_state(self):
        at, canpolpaint, canlatroll, cangrind, free = self.get_fluents(
            ['at', 'canpolpaint', 'canlatroll', 'cangrind', 'free'])
        piece_list = self.get_objects(['x'+str(i) for i in range(self.object_amount)])
        machine_list = self.get_objects(['m'+str(i) for i in range(self.object_amount)])

        for i in range(0, self.object_amount):
            self.problem.set_initial_value(free(machine_list[i]), True)

            if i%2 == 0:
                self.problem.set_initial_value(canlatroll(machine_list[i]), True)
                self.problem.set_initial_value(cangrind(machine_list[i]), True)
                self.problem.set_initial_value(at(piece_list[i], machine_list[i]), True)

            else:
                self.problem.set_initial_value(canpolpaint(machine_list[i]), True)
                self.problem.set_initial_value(at(piece_list[i], machine_list[i-1]), True)




    def add_goal(self, deadline):
        shaped, painted, smooth, polished, free = self.get_fluents(['shaped', 'painted', 'smooth', 'polished', 'free'])
        piece_list = self.get_objects(['x'+str(i) for i in range(self.object_amount)])
        machine_list = self.get_objects(['m'+str(i) for i in range(self.object_amount)])

        for i in range(0, self.object_amount):
            self.problem.add_goal(free(machine_list[i]))
            if i % 2 == 0:
                self.problem.add_goal(shaped(piece_list[i]))
                self.problem.add_goal(smooth(piece_list[i]))
            else:
                self.problem.add_goal(painted(piece_list[i]))
                self.problem.add_goal(polished(piece_list[i]))


        deadline_timing = Timing(delay=deadline, timepoint=Timepoint(TimepointKind.START))
        self.problem.set_deadline(deadline_timing)

    def actions(self):
        self.polish_action()
        self.spraypaint_action()
        self.immersionpaint_action()
        self.lathe_action()
        self.grind_action()
        self.buyimmersion_action()
        self.place_action()
        self.move_action()

    def immersionpaint_prob(self, piece, machine):
        hasimmersion, painted = self.get_fluents(['hasimmersion', 'painted', ])

        def immersionpaint_probability(state, actual_params):
            piece_param = actual_params.get(piece)
            machine_param = actual_params.get(machine)
            return {0.57: {painted(piece_param): True, hasimmersion(machine_param): True},
                    0.38: {painted(piece_param): True, hasimmersion(machine_param): False},
                    0.02: {hasimmersion(machine_param): False},
                    0.03: {hasimmersion(machine_param): True}}

        return immersionpaint_probability

    def lathe_prob(self, piece):
        shaped, painted, smooth = self.get_fluents(['shaped', 'painted', 'smooth'])

        def lathe_probability(state, actual_params):
            piece_param = actual_params.get(piece)
            p = 0.9

            # return {p: {shaped(piece_param): True, painted(piece_param): False, smooth(piece_param): False}, 1 - p: {}}
            return {p: {shaped(piece_param): True}, 1 - p: {}}
            # TODO: changed to be not probabilistic effect

        return lathe_probability

    def action_prob(self, p, fluent, piece):
        def probability(state, actual_params):
            piece_param = actual_params.get(piece)

            return {p[0]: {fluent(piece_param): True}, p[1]: {}}

        return probability

    def move_prob(self, piece, machine1, machine2):
        on, at, free = self.get_fluents(['on', 'at', 'free'])

        def move_probability(state, actual_params):
            piece_param = actual_params.get(piece)
            machine1_param = actual_params.get(machine1)
            machine2_param = actual_params.get(machine2)
            predicates = state.predicates
            if on(piece_param, machine1_param) in predicates:
                p = 0.9
                return {p: {at(piece_param, machine2_param): True, at(piece_param, machine1_param): False,
                            on(piece_param, machine1_param): False, free(machine1_param): True},
                        1 - p: {on(piece_param, machine1_param): False, free(machine1_param): True,
                                at(piece_param, machine1_param): True}}
            else:
                p = 0.9
                return {p: {at(piece_param, machine2_param): True, at(piece_param, machine1_param): False},
                        1 - p: {at(piece_param, machine1_param): True}}

        return move_probability

    def polish_action(self):
        """ Polish Action """

        canpolpaint, on, at, polished = self.get_fluents(['canpolpaint', 'on', 'at', 'polished'])

        polish = unified_planning.model.action.DurativeAction('polish', piece=self.userTypes['Piece'],
                                                              machine=self.userTypes['Machine'])
        polish.set_fixed_duration(10)
        machine = polish.parameter('machine')
        piece = polish.parameter('piece')
        polish.add_precondition(StartPreconditionTiming(), canpolpaint(machine), True)
        polish.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)

        if self.kind == 'regular':
            polish.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)

        polish.add_probabilistic_effect([polished(piece)], self.action_prob(p=[0.9, 0.1], fluent=polished, piece=piece))
        self.problem.add_action(polish)

    def spraypaint_action(self):
        """ Spraypaint Action """
        canpolpaint, on, at, painted = self.get_fluents(['canpolpaint', 'on', 'at', 'painted'])

        spraypaint = unified_planning.model.action.DurativeAction('spraypaint', piece=self.userTypes['Piece'],
                                                                  machine=self.userTypes['Machine'])
        spraypaint.set_fixed_duration(6)
        machine = spraypaint.parameter('machine')
        piece = spraypaint.parameter('piece')
        spraypaint.add_precondition(StartPreconditionTiming(), canpolpaint(machine), True)
        spraypaint.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)
        if self.kind == 'regular':
            spraypaint.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)

        spraypaint.add_probabilistic_effect([painted(piece)],
                                            self.action_prob(p=[0.8, 0.2], fluent=painted, piece=piece))
        self.problem.add_action(spraypaint)

    def immersionpaint_action(self):
        """ Immersionpaint Action """
        canpolpaint, on, at, hasimmersion, painted = self.get_fluents(
            ['canpolpaint', 'on', 'at', 'hasimmersion', 'painted'])

        immersionpaint = unified_planning.model.action.DurativeAction('immersionpaint', piece=self.userTypes['Piece'],
                                                                      machine=self.userTypes['Machine'])
        immersionpaint.set_fixed_duration(4)
        machine = immersionpaint.parameter('machine')
        piece = immersionpaint.parameter('piece')
        immersionpaint.add_precondition(StartPreconditionTiming(), canpolpaint(machine), True)
        immersionpaint.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)

        if self.kind == 'regular':
            immersionpaint.add_precondition(StartPreconditionTiming(), hasimmersion(machine), True)
            immersionpaint.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)
            immersionpaint.add_start_effect(hasimmersion(machine), False)

        if self.kind == 'combination':
            immersionpaint.add_precondition(OverallPreconditionTiming(), hasimmersion(machine), True)

        immersionpaint.add_probabilistic_effect([painted(piece), hasimmersion(machine)],
                                                self.immersionpaint_prob(piece, machine))
        self.problem.add_action(immersionpaint)

    def lathe_action(self):
        """ Lathe Action """
        canlatroll, on, at, shaped, painted, smooth = self.get_fluents(
            ['canlatroll', 'on', 'at', 'shaped', 'painted', 'smooth'])

        lathe = unified_planning.model.action.DurativeAction('lathe', piece=self.userTypes['Piece'],
                                                             machine=self.userTypes['Machine'])
        lathe.set_fixed_duration(2)
        machine = lathe.parameter('machine')
        piece = lathe.parameter('piece')
        lathe.add_precondition(StartPreconditionTiming(), canlatroll(machine), True)
        lathe.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)

        if self.kind == 'regular':
            lathe.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)

        lathe.add_effect(painted(piece), False)  # TODO: changed to be not probabilistic effect
        lathe.add_effect(smooth(piece), False)   # TODO: changed to be not probabilistic effect
        # lathe.add_probabilistic_effect([shaped(piece), painted(piece), smooth(piece)], self.lathe_prob(piece))
        lathe.add_probabilistic_effect([shaped(piece)], self.lathe_prob(piece))
        self.problem.add_action(lathe)

    def grind_action(self):
        """ Grind Action """
        cangrind, on, at, smooth = self.get_fluents(['cangrind', 'on', 'at', 'smooth'])

        grind = unified_planning.model.action.DurativeAction('grind', piece=self.userTypes['Piece'],
                                                             machine=self.userTypes['Machine'])
        grind.set_fixed_duration(3)
        machine = grind.parameter('machine')
        piece = grind.parameter('piece')
        grind.add_precondition(StartPreconditionTiming(), cangrind(machine), True)
        grind.add_precondition(OverallPreconditionTiming(), on(piece, machine), True)
        if self.kind == 'regular':
            grind.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)

        grind.add_probabilistic_effect([smooth(piece)], self.action_prob(p=[0.9, 0.1], fluent=smooth, piece=piece))
        self.problem.add_action(grind)

    def buyimmersion_action(self):
        """ Buyimmersion Action """
        hasimmersion = self.problem.fluent_by_name('hasimmersion')

        buyimmersion = unified_planning.model.action.DurativeAction('buyimmersion', machine=self.userTypes['Machine'])
        buyimmersion.set_fixed_duration(5)
        machine = buyimmersion.parameter('machine')

        buyimmersion.add_effect(hasimmersion(machine), True)
        self.problem.add_action(buyimmersion)

    def place_action(self):
        """ Place Action """
        on, at, free = self.get_fluents(['on', 'at', 'free'])

        place = unified_planning.model.action.DurativeAction('place', piece=self.userTypes['Piece'],
                                                             machine=self.userTypes['Machine'])
        place.set_fixed_duration(1)
        machine = place.parameter('machine')
        piece = place.parameter('piece')
        place.add_precondition(OverallPreconditionTiming(), at(piece, machine), True)
        if self.kind == 'regular':
            place.add_precondition(StartPreconditionTiming(), free(machine), True)
            place.add_start_effect(free(machine), False)

        if self.kind == 'combination':
            place.add_precondition(OverallPreconditionTiming(), free(machine), True)
            place.add_effect(free(machine), False)

        place.add_effect(on(piece, machine), True)

        self.problem.add_action(place)

    def move_action(self):
        """ Move Action """
        on, at, free = self.get_fluents(['on', 'at', 'free'])

        move = unified_planning.model.action.DurativeAction('move', piece=self.userTypes['Piece'],
                                                            machine1=self.userTypes['Machine'],
                                                            machine2=self.userTypes['Machine'])
        move.set_fixed_duration(3)
        machine1 = move.parameter('machine1')
        machine2 = move.parameter('machine2')
        piece = move.parameter('piece')
        move.add_precondition(ParamPrecondition(), Equals(machine1, machine2), False)
        if self.kind == 'regular':
            move.add_precondition(StartPreconditionTiming(), at(piece, machine1), True)
            move.add_start_effect(at(piece, machine1), False)
        if self.kind == 'combination':
            move.add_precondition(OverallPreconditionTiming(), at(piece, machine1), True)

        move.add_probabilistic_effect([on(piece, machine1), free(machine2), at(piece, machine1), at(piece, machine2)],
                                      self.move_prob(piece, machine1, machine2))
        self.problem.add_action(move)

    def remove_actions(self, converted_problem):
        on, at = self.get_fluents(['on', 'at'])
        piece_list = self.get_objects(['x' + str(i) for i in range(self.object_amount)])
        machine_list = self.get_objects(['m' + str(i) for i in range(self.object_amount)])

        list(itertools.product(piece_list, machine_list))

        not_allowed_predicates = []
        for i in range(0, self.object_amount):
            piece_with_machines = list(itertools.product([piece_list[i]], machine_list))
            result_tuples = list(itertools.combinations(piece_with_machines, 2))

            # a piece can't be `on` two different machines
            on_set = [{on(*combination[0]), on(*combination[1])} for combination in result_tuples]
            # a piece can't be `at` two different machines
            at_set = [{at(*combination[0]), at(*combination[1])} for combination in result_tuples]
            # a piece can't be `on` and `at different machines
            on_at_set = [{on(*combination[0]), at(*combination[1])} for combination in result_tuples]
            at_on_set = [{at(*combination[0]), on(*combination[1])} for combination in result_tuples]

            not_allowed_predicates += on_set + at_set + on_at_set + at_on_set

            # a machine can't carry (`on`) two different pieces
            machine_with_pieces = list(itertools.product(piece_list, [machine_list[i]]))
            result_tuples = list(itertools.combinations(machine_with_pieces, 2))
            on_set = [{on(*combination[0]), on(*combination[1])} for combination in result_tuples]

            not_allowed_predicates += on_set


        for a in converted_problem.actions[:]:
            if isinstance(a, unified_planning.engines.CombinationAction):
                for p in not_allowed_predicates:
                    if p.issubset(a.pos_preconditions):
                        converted_problem.actions.remove(a)
                        break

    def allowed_actions(self, actions, potential_action):
        on, at = self.get_fluents(['on', 'at'])
        piece_list = self.get_objects(['x' + str(i) for i in range(self.object_amount)])
        machine_list = self.get_objects(['m' + str(i) for i in range(self.object_amount)])

        list(itertools.product(piece_list, machine_list))

        not_allowed_predicates = []
        for i in range(0, self.object_amount):
            piece_with_machines = list(itertools.product([piece_list[i]], machine_list))
            result_tuples = list(itertools.combinations(piece_with_machines, 2))

            # a piece can't be `on` two different machines
            on_set = [{on(*combination[0]), on(*combination[1])} for combination in result_tuples]
            # a piece can't be `at` two different machines
            at_set = [{at(*combination[0]), at(*combination[1])} for combination in result_tuples]
            # a piece can't be `on` and `at different machines
            on_at_set = [{on(*combination[0]), at(*combination[1])} for combination in result_tuples]
            at_on_set = [{at(*combination[0]), on(*combination[1])} for combination in result_tuples]

            not_allowed_predicates += on_set + at_set + on_at_set + at_on_set

            # a machine can't carry (`on`) two different pieces
            machine_with_pieces = list(itertools.product(piece_list, [machine_list[i]]))
            result_tuples = list(itertools.combinations(machine_with_pieces, 2))
            on_set = [{on(*combination[0]), on(*combination[1])} for combination in result_tuples]

            not_allowed_predicates += on_set

        pos_precondition_combination = potential_action.pos_preconditions
        for a in actions[:]:
            pos_precondition_combination = pos_precondition_combination.union(a.pos_preconditions)

        for p in not_allowed_predicates:
                if p.issubset(pos_precondition_combination):
                    return False

        return True


    # run_regular(deadline=27, search_time=15, search_depth=40, selection_type='avg')
# run_combination(solver='rtdp', deadline=80, search_time=10, search_depth=40)
# run_combination(solver='mcts', deadline=27, search_time=60, search_depth=40, selection_type='avg')
