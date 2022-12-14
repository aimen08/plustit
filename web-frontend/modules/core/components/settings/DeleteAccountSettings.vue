<template>
  <div>
    <h2 class="box__title">{{ $t('deleteAccountSettings.title') }}</h2>

    <p>
      {{
        $t('deleteAccountSettings.description', {
          days: settings.account_deletion_grace_delay,
        })
      }}
    </p>

    <div v-if="$fetchState.pending" class="loading__wrapper">
      <div class="loading loading-absolute-center" />
    </div>

    <Alert
      v-else-if="$fetchState.error"
      type="error"
      icon="exclamation"
      :title="$t('deleteAccountSettings.groupLoadingError')"
    >
      {{ $t('deleteAccountSettings.groupLoadingErrorDescription') }}
    </Alert>

    <div v-else-if="orphanGroups.length" class="delete-section">
      <div class="delete-section__label">
        <div class="delete-section__label-icon">
          <i class="fas fa-exclamation"></i>
        </div>
        {{ $t('deleteAccountSettings.orphanGroups') }}
      </div>
      <p class="delete-section__description">
        {{ $t('deleteAccountSettings.groupNoticeDescription') }}
      </p>
      <ul class="delete-section__list">
        <li v-for="group in orphanGroups" :key="group.id">
          <i class="delete-section__list-icon fas fa-users"></i>
          {{ group.name }}
          <small>
            {{
              $tc(
                'deleteAccountSettings.orphanGroupMemberCount',
                groupMembers[group.id].length,
                {
                  count: groupMembers[group.id].length,
                }
              )
            }}</small
          >
        </li>
      </ul>
    </div>

    <Error :error="error"></Error>

    <form
      v-if="!success"
      class="delete-account-settings__form"
      @submit.prevent="deleteAccount"
    >
      <div class="control">
        <label class="control__label">{{
          $t('deleteAccountSettings.password')
        }}</label>
        <div class="control__elements">
          <PasswordInput
            v-model="account.password"
            :validation-state="$v.account.password"
          />
        </div>
      </div>
      <div class="control">
        <label class="control__label">{{
          $t('deleteAccountSettings.passwordConfirm')
        }}</label>
        <div class="control__elements">
          <input
            v-model="account.passwordConfirm"
            :class="{ 'input--error': $v.account.passwordConfirm.$error }"
            type="password"
            class="input input--large"
            @blur="$v.account.passwordConfirm.$touch()"
          />
          <div v-if="$v.account.passwordConfirm.$error" class="error">
            {{ $t('deleteAccountSettings.repeatPasswordMatchError') }}
          </div>
        </div>
      </div>
      <div class="actions actions--right">
        <button
          :class="{ 'button--loading': loading }"
          class="button button--large button--error"
          :disabled="loading"
        >
          {{ $t('deleteAccountSettings.submitButton') }}
          <i class="fas fa-trash"></i>
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { notifyIf } from '@baserow/modules/core/utils/error'
import { mapGetters } from 'vuex'
import { sameAs } from 'vuelidate/lib/validators'

import { ResponseErrorMessage } from '@baserow/modules/core/plugins/clientHandler'
import error from '@baserow/modules/core/mixins/error'
import AuthService from '@baserow/modules/core/services/auth'
import PasswordInput from '@baserow/modules/core/components/helpers/PasswordInput'
import { passwordValidation } from '@baserow/modules/core/validators'
import GroupService from '@baserow/modules/core/services/group'

export default {
  components: { PasswordInput },
  mixins: [error],
  data() {
    return {
      loading: false,
      success: false,
      account: {
        password: '',
        passwordConfirm: '',
      },
      groupMembers: {},
    }
  },
  async fetch() {
    this.groupMembers = Object.fromEntries(
      await Promise.all(
        this.sortedGroups
          .filter(({ permissions }) => permissions === 'ADMIN')
          .map(async ({ id: groupId }) => {
            const { data } = await GroupService(this.$client).fetchAllUsers(
              groupId
            )
            return [
              groupId,
              data.filter(({ user_id: userId }) => userId !== this.userId),
            ]
          })
      )
    )
  },
  computed: {
    ...mapGetters({
      userId: 'auth/getUserId',
      settings: 'settings/get',
      sortedGroups: 'group/getAllSorted',
    }),
    orphanGroups() {
      return this.sortedGroups.filter(
        ({ id: groupId }) =>
          this.groupMembers[groupId] &&
          this.groupMembers[groupId].every(
            ({ permissions }) => permissions !== 'ADMIN'
          )
      )
    },
  },
  methods: {
    async logoff() {
      await this.$store.dispatch('auth/logoff')
      this.$nuxt.$router.push({ name: 'login' })
      this.$store.dispatch('notification/success', {
        title: this.$t('deleteAccountSettings.accountDeletedSuccessTitle'),
        message: this.$t('deleteAccountSettings.accountDeletedSuccessMessage'),
      })
    },
    async loadGroupMembers() {
      this.groupLoading = true
      try {
        this.groupMembers = Object.fromEntries(
          await Promise.all(
            this.sortedGroups
              .filter(({ permissions }) => permissions === 'ADMIN')
              .map(async ({ id: groupId }) => {
                const { data } = await GroupService(this.$client).fetchAllUsers(
                  groupId
                )
                return [
                  groupId,
                  data.filter(({ user_id: userId }) => userId !== this.userId),
                ]
              })
          )
        )
      } catch (error) {
        notifyIf(error, 'group')
      } finally {
        this.groupLoading = false
      }
    },
    async deleteAccount() {
      this.$v.$touch()

      if (this.$v.$invalid) {
        return
      }

      this.loading = true
      this.hideError()

      try {
        await AuthService(this.$client).deleteAccount(this.account.password)
        this.success = true
        this.logoff()
      } catch (error) {
        this.handleError(error, 'deleteAccount', {
          ERROR_INVALID_PASSWORD: new ResponseErrorMessage(
            this.$t('deleteAccountSettings.errorInvalidPasswordTitle'),
            this.$t('deleteAccountSettings.errorInvalidPasswordMessage')
          ),
          ERROR_USER_IS_LAST_ADMIN: new ResponseErrorMessage(
            this.$t('deleteAccountSettings.errorUserIsLastAdminTitle'),
            this.$t('deleteAccountSettings.errorUserIsLastAdminMessage')
          ),
        })
      } finally {
        this.loading = false
      }
    },
  },
  validations: {
    account: {
      passwordConfirm: {
        sameAsPassword: sameAs('password'),
      },
      password: passwordValidation,
    },
  },
}
</script>
